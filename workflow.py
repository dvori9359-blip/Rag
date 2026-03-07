"""
שלב ב' — ארכיטקטורת Event-Driven Workflow
LLM: Cohere command-r-08-2024 (ללא OpenAI)
"""

import os
import ssl
import warnings
import urllib3
from datetime import datetime
from dotenv import load_dotenv

ssl._create_default_https_context = ssl._create_unverified_context
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
os.environ['PYTHONHTTPSVERIFY'] = "0"
os.environ['CURL_CA_BUNDLE'] = ""
os.environ['REQUESTS_CA_BUNDLE'] = ""

import httpx
_original_init = httpx.Client.__init__
def _patched_init(self, *args, **kwargs):
    kwargs['verify'] = False
    _original_init(self, *args, **kwargs)
httpx.Client.__init__ = _patched_init

_original_async_init = httpx.AsyncClient.__init__
def _patched_async_init(self, *args, **kwargs):
    kwargs['verify'] = False
    _original_async_init(self, *args, **kwargs)
httpx.AsyncClient.__init__ = _patched_async_init

load_dotenv()
warnings.filterwarnings('ignore')

from llama_index.core.workflow import Workflow, StartEvent, StopEvent, Event, step, Context
from llama_index.core.workflow.drawing import draw_all_possible_flows
from llama_index.core import Settings, VectorStoreIndex, StorageContext
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.postprocessor import SimilarityPostprocessor
from llama_index.core.response_synthesizers import get_response_synthesizer
from llama_index.embeddings.cohere import CohereEmbedding
from llama_index.llms.cohere import Cohere
from llama_index.vector_stores.pinecone import PineconeVectorStore
from pinecone import Pinecone
import gradio as gr
import asyncio

try:
    asyncio.get_running_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())

COHERE_API_KEY   = os.getenv("COHERE_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

if not all([COHERE_API_KEY, PINECONE_API_KEY]):
    raise ValueError("נא לוודא COHERE_API_KEY, PINECONE_API_KEY ב-.env")

Settings.embed_model = CohereEmbedding(api_key=COHERE_API_KEY, model_name="embed-multilingual-v3.0")
Settings.llm = Cohere(api_key=COHERE_API_KEY, model="command-r-08-2024")

pc = Pinecone(api_key=PINECONE_API_KEY, ssl_verify=False)
pinecone_index  = pc.Index("agentic-docs-index")
vector_store    = PineconeVectorStore(pinecone_index=pinecone_index)
index           = VectorStoreIndex.from_vector_store(vector_store)

print("[OK] מחובר לאינדקס Pinecone הקיים")


# ===== Events =====
class QueryEvent(Event):
    query: str

class ResultsEvent(Event):
    query: str
    nodes: list

class NoResultsEvent(Event):
    query: str
    reason: str

class SynthesizeEvent(Event):
    query: str
    nodes: list

class LowConfidenceEvent(Event):
    query: str
    best_score: float


# ===== Workflow =====
class RAGWorkflow(Workflow):

    @step
    async def validate_input(self, ctx: Context, ev: StartEvent) -> QueryEvent | StopEvent:
        query = ev.get("query", "")

        if not query or not query.strip():
            return StopEvent(result="❌ שאלה ריקה — נא להזין שאלה.")
        query = query.strip()
        if len(query) < 3:
            return StopEvent(result="❌ השאלה קצרה מדי.")
        if len(query) > 1000:
            return StopEvent(result="❌ השאלה ארוכה מדי.")

        await ctx.set_data("original_query", query)
        await ctx.set_data("started_at", datetime.now().isoformat())
        print(f"[OK] [validate] שאלה תקינה: '{query}'")
        return QueryEvent(query=query)

    @step
    async def retrieve(self, ctx: Context, ev: QueryEvent) -> ResultsEvent | NoResultsEvent:
        print(f"[SEARCH] [retrieve] מחפש: '{ev.query}'")
        retriever = VectorIndexRetriever(index=index, similarity_top_k=5)
        try:
            nodes = retriever.retrieve(ev.query)
        except Exception as e:
            return NoResultsEvent(query=ev.query, reason=f"שגיאה בחיפוש: {str(e)}")

        if not nodes:
            return NoResultsEvent(query=ev.query, reason="לא נמצאו תוצאות")

        print(f"   נמצאו {len(nodes)} תוצאות")
        await ctx.set_data("num_before_filter", len(nodes))
        return ResultsEvent(query=ev.query, nodes=nodes)

    @step
    async def postprocess(self, ctx: Context, ev: ResultsEvent | NoResultsEvent) -> SynthesizeEvent | LowConfidenceEvent | StopEvent:
        if isinstance(ev, NoResultsEvent):
            return StopEvent(result=f"לא נמצא מידע רלוונטי.\nסיבה: {ev.reason}")

        processor      = SimilarityPostprocessor(similarity_cutoff=0.5)
        filtered_nodes = processor.postprocess_nodes(ev.nodes)
        print(f"   [postprocess] {len(filtered_nodes)}/{len(ev.nodes)} nodes עברו סינון")

        if not filtered_nodes:
            best_score = max((n.score for n in ev.nodes if n.score), default=0.0)
            return LowConfidenceEvent(query=ev.query, best_score=round(best_score, 3))

        await ctx.set_data("num_after_filter", len(filtered_nodes))
        return SynthesizeEvent(query=ev.query, nodes=filtered_nodes)

    @step
    async def handle_low_confidence(self, ctx: Context, ev: LowConfidenceEvent) -> StopEvent:
        return StopEvent(
            result=(
                f"נמצאו תוצאות אך רמת הביטחון נמוכה מדי (best score: {ev.best_score}).\n"
                "[TIP] נסי לנסח את השאלה בצורה אחרת."
            )
        )

    @step
    async def synthesize(self, ctx: Context, ev: SynthesizeEvent) -> StopEvent:
        print(f"[LLM] [synthesize] מנסח תשובה מ-{len(ev.nodes)} nodes...")
        synthesizer = get_response_synthesizer(response_mode="compact", use_async=True)
        response    = await synthesizer.asynthesize(ev.query, nodes=ev.nodes)
        answer      = str(response)

        seen = set()
        sources_text = ""
        for i, node in enumerate(ev.nodes[:3], 1):
            tool  = node.metadata.get('tool', 'לא ידוע')
            src   = node.metadata.get('source_file', 'לא ידוע')
            score = round(node.score, 3) if node.score else 'N/A'
            key   = f"{tool}:{src}"
            if key not in seen:
                sources_text += f"{i}. **{tool}** › {src} (score: {score})\n"
                seen.add(key)

        if sources_text:
            answer += f"\n\n---\n📚 **מקורות:**\n{sources_text}"

        original_query = await ctx.get_data("original_query", default="")
        before = await ctx.get_data("num_before_filter", default=0)
        after  = await ctx.get_data("num_after_filter", default=0)
        print(f"[DONE] הושלם | '{original_query}' | {after}/{before} nodes")

        return StopEvent(result=answer)


workflow = RAGWorkflow(timeout=60, verbose=False)


def visualize_workflow(workflow_instance: Workflow, output_path: str = "workflow_map.html") -> str:
    draw_all_possible_flows(workflow_instance, filename=output_path)
    print(f"[OK] נוצר קובץ תרשים זרימה: {output_path}")
    return output_path


def run_workflow_sync(query: str) -> str:
    import threading
    result_container = []
    exception_container = []

    def target():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(workflow.run(query=query))
            result_container.append(str(result))
        except Exception as e:
            exception_container.append(str(e))
        finally:
            loop.close()

    t = threading.Thread(target=target, daemon=True)
    t.start()
    t.join(timeout=90)

    if exception_container:
        return f"שגיאה: {exception_container[0]}"
    if result_container:
        return result_container[0]
    return "שגיאה: timeout — לא התקבלה תשובה בזמן"


async def chat_function(message, history):
    if not message or not message.strip():
        return "נא להזין שאלה."
    try:
        result = await workflow.run(query=message)
        return str(result)
    except Exception as e:
        return f"Error during workflow execution: {str(e)}"


demo = gr.ChatInterface(
    fn=chat_function,
    title="🔍 Agentic Docs RAG — Event-Driven Workflow",
    description="שלב ב': ולידציה ← חיפוש ← סינון ← סינתזה",
    examples=[
        "מה הצבע העיקרי שנבחר לדיזיין?",
        "האם קיימת הנחיה לגבי שימוש ב-RTL?",
        "איזה רכיב הוגדר כרגיש במיוחד?",
    ]
)

if __name__ == "__main__":
    import sys
    if "--map" in sys.argv:
        visualize_workflow(workflow)
        raise SystemExit(0)
    demo.launch(share=False)