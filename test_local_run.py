"""
Local validation script to bypass Pinecone and verify metadata + workflow.
"""

import os
import ssl
import warnings
import urllib3
from datetime import datetime

ssl._create_default_https_context = ssl._create_unverified_context
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
os.environ["PYTHONHTTPSVERIFY"] = "0"
os.environ["CURL_CA_BUNDLE"] = ""
os.environ["REQUESTS_CA_BUNDLE"] = ""

import httpx
_original_init = httpx.Client.__init__

def _patched_init(self, *args, **kwargs):
    kwargs["verify"] = False
    _original_init(self, *args, **kwargs)

httpx.Client.__init__ = _patched_init

_original_async_init = httpx.AsyncClient.__init__

def _patched_async_init(self, *args, **kwargs):
    kwargs["verify"] = False
    _original_async_init(self, *args, **kwargs)

httpx.AsyncClient.__init__ = _patched_async_init

warnings.filterwarnings("ignore")

from dotenv import load_dotenv
from llama_index.core import SimpleDirectoryReader, Settings, VectorStoreIndex, StorageContext
from llama_index.core.node_parser import MarkdownNodeParser
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.postprocessor import SimilarityPostprocessor
from llama_index.core.response_synthesizers import get_response_synthesizer
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.workflow import Workflow, StartEvent, StopEvent, Event, step, Context
from llama_index.core.workflow.drawing import draw_all_possible_flows
from llama_index.core.vector_stores import SimpleVectorStore
from llama_index.embeddings.cohere import CohereEmbedding
from llama_index.llms.cohere import Cohere
import asyncio

load_dotenv()

COHERE_API_KEY = os.getenv("COHERE_API_KEY")
if not COHERE_API_KEY:
    raise ValueError("נא לוודא COHERE_API_KEY ב-.env")

Settings.embed_model = CohereEmbedding(api_key=COHERE_API_KEY, model_name="embed-multilingual-v3.0")
Settings.llm = Cohere(api_key=COHERE_API_KEY, model="command-r-08-2024")


# ===== Local Data Loading =====

def load_documents():
    tools_paths = {
        "cursor": "./.cursor",
        "claude_code": "./.claude",
        "windsurf": "./.windsurf",
        "kiro": "./.kiro",
        "docs_ai": "./docs_ai",
    }

    all_documents = []
    for tool_name, tool_path in tools_paths.items():
        if not os.path.exists(tool_path):
            continue

        docs = SimpleDirectoryReader(input_dir=tool_path, recursive=True, required_exts=[".md"]).load_data()
        for doc in docs:
            doc.metadata["tool"] = tool_name
            doc.metadata["source_file"] = doc.metadata.get("file_name", "")
            doc.metadata["file_path"] = doc.metadata.get("file_path", "")
            doc.metadata["loaded_at"] = datetime.now().isoformat()
            first_line = doc.text.split("\n")[0].strip("#").strip()
            doc.metadata["title"] = first_line[:100] if first_line else doc.metadata["source_file"]
        all_documents.extend(docs)

    if not all_documents:
        raise ValueError("❌ לא נמצאו מסמכים!")
    return all_documents


# ===== Local Index with section_header =====

def build_local_index():
    documents = load_documents()
    node_parser = MarkdownNodeParser()
    nodes = node_parser.get_nodes_from_documents(documents)

    for node in nodes:
        header_path = node.metadata.get("header_path")
        if isinstance(header_path, list):
            section_header = " > ".join([h for h in header_path if h])
        else:
            section_header = header_path or ""
        node.metadata["section_header"] = section_header

    vector_store = SimpleVectorStore()
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    index = VectorStoreIndex(
        nodes,
        storage_context=storage_context,
        show_progress=True,
    )
    return index, nodes


# ===== Metadata Verification =====

def verify_metadata(nodes, sample_size: int = 3):
    print("\n🔎 Metadata sample (section_header):")
    for node in nodes[:sample_size]:
        print({
            "tool": node.metadata.get("tool"),
            "file_path": node.metadata.get("file_path"),
            "section_header": node.metadata.get("section_header"),
        })


# ===== Local Workflow =====
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


class LocalRAGWorkflow(Workflow):
    def __init__(self, nodes, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._nodes = nodes

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

        await ctx.set("original_query", query)
        await ctx.set("started_at", datetime.now().isoformat())
        return QueryEvent(query=query)

    @step
    async def retrieve(self, ctx: Context, ev: QueryEvent) -> ResultsEvent | NoResultsEvent:
        nodes = self._nodes[:5]
        if not nodes:
            return NoResultsEvent(query=ev.query, reason="לא נמצאו תוצאות")

        await ctx.set("num_before_filter", len(nodes))
        return ResultsEvent(query=ev.query, nodes=nodes)

    @step
    async def postprocess(self, ctx: Context, ev: ResultsEvent | NoResultsEvent) -> SynthesizeEvent | LowConfidenceEvent | StopEvent:
        if isinstance(ev, NoResultsEvent):
            return StopEvent(result=f"לא נמצא מידע רלוונטי.\nסיבה: {ev.reason}")

        processor = SimilarityPostprocessor(similarity_cutoff=0.5)
        filtered_nodes = processor.postprocess_nodes(ev.nodes)

        if not filtered_nodes:
            best_score = max((n.score for n in ev.nodes if n.score), default=0.0)
            return LowConfidenceEvent(query=ev.query, best_score=round(best_score, 3))

        await ctx.set("num_after_filter", len(filtered_nodes))
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
        answer = f"נמצאו {len(ev.nodes)} מקטעים רלוונטיים עבור: {ev.query}"
        return StopEvent(result=answer)


def visualize_workflow(workflow_instance: Workflow, output_path: str = "workflow_map.html") -> str:
    draw_all_possible_flows(workflow_instance, filename=output_path)
    print(f"[OK] נוצר קובץ תרשים זרימה: {output_path}")
    return output_path


def run_workflow_sync(workflow_instance: Workflow, query: str) -> str:
    try:
        async def _runner():
            return workflow_instance.run(query=query)

        result = asyncio.run(_runner())
        return str(result)
    except Exception as e:
        import traceback
        print("\n⚠️ Workflow error traceback:")
        print(traceback.format_exc())
        return f"שגיאה: {str(e)}"


if __name__ == "__main__":
    index, nodes = build_local_index()
    verify_metadata(nodes)

    workflow = LocalRAGWorkflow(nodes=nodes, timeout=60, verbose=False)
    visualize_workflow(workflow)

    # Run a quick query locally
    answer = run_workflow_sync(workflow, "מה הצבע העיקרי שנבחר לדיזיין?")
    print("\n✅ Workflow local run result:")
    print(answer)
