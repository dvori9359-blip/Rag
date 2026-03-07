import os
import ssl
import warnings
import urllib3
from datetime import datetime
from dotenv import load_dotenv

# ===== עקיפת SSL =====
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

import gradio as gr
from pinecone import Pinecone, ServerlessSpec
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, StorageContext, Settings
from llama_index.core.node_parser import MarkdownNodeParser
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.postprocessor import SimilarityPostprocessor
from llama_index.core.response_synthesizers import get_response_synthesizer
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.embeddings.cohere import CohereEmbedding
from llama_index.llms.cohere import Cohere
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.core.vector_stores import SimpleVectorStore

# ===== בדיקת מפתחות =====
COHERE_API_KEY   = os.getenv("COHERE_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

if not all([COHERE_API_KEY, PINECONE_API_KEY]):
    raise ValueError("נא לוודא שהמפתחות מוגדרים בקובץ .env: COHERE_API_KEY, PINECONE_API_KEY")

# ===== הגדרת מודלים — Cohere בלבד =====
Settings.embed_model = CohereEmbedding(
    api_key=COHERE_API_KEY,
    model_name="embed-multilingual-v3.0"
)
Settings.llm = Cohere(
    api_key=COHERE_API_KEY,
    model="command-r-08-2024"
)

def get_vector_store():
    if os.getenv("LOCAL_VECTOR_STORE", "").lower() in {"1", "true", "yes"}:
        print("🧪 LOCAL_VECTOR_STORE=1 → משתמש ב-SimpleVectorStore")
        return SimpleVectorStore()

    try:
        pc = Pinecone(api_key=PINECONE_API_KEY, ssl_verify=False)
        index_name = "agentic-docs-index"
        embedding_dim = 1024

        existing = [idx.name for idx in pc.list_indexes()]
        if index_name in existing:
            desc = pc.describe_index(index_name)
            if desc.dimension != embedding_dim:
                print("⚠️  מוחק אינדקס עם ממד שגוי ויוצר מחדש...")
                pc.delete_index(index_name)
                pc.create_index(
                    name=index_name,
                    dimension=embedding_dim,
                    metric="cosine",
                    spec=ServerlessSpec(cloud="aws", region="us-east-1"),
                )
            else:
                print(f"✅ האינדקס '{index_name}' קיים ותקין")
        else:
            print(f"📦 יוצר אינדקס חדש '{index_name}'...")
            pc.create_index(
                name=index_name,
                dimension=embedding_dim,
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1"),
            )

        pinecone_index = pc.Index(index_name)
        return PineconeVectorStore(pinecone_index=pinecone_index)
    except Exception as e:
        print(f"⚠️  Pinecone לא זמין, עובר ל-SimpleVectorStore. סיבה: {str(e)}")
        return SimpleVectorStore()


# ===== שלב 1: Loading =====
def load_documents():
    from pathlib import Path
    base_dir = os.path.abspath(os.getcwd())
    tools_paths = {
        "cursor":      os.path.join(base_dir, ".cursor"),
        "claude_code": os.path.join(base_dir, ".claude"),
        "windsurf":    os.path.join(base_dir, ".windsurf"),
        "kiro":        os.path.join(base_dir, ".kiro"),
        "docs_ai":     os.path.join(base_dir, "docs_ai"),
    }

    all_documents = []
    print("\n📂 שלב 1 - Loading: טוען קבצי .md מכלי Agentic Coding...")

    for tool_name, tool_path in tools_paths.items():
        if not os.path.exists(tool_path):
            print(f"  ⏭️  {tool_name} ({tool_path}) לא קיים, מדלג...")
            continue

        print(f"  📂 טוען מ-{tool_name}...")
        try:
            md_files = [str(p) for p in Path(tool_path).rglob("*.md")]
            if not md_files:
                print(f"    ⏭️  לא נמצאו קבצי .md ב-{tool_name}, מדלג...")
                continue

            docs = SimpleDirectoryReader(input_files=md_files).load_data()

            for doc in docs:
                doc.metadata["tool"]        = tool_name
                doc.metadata["source_file"] = doc.metadata.get("file_name", "")
                doc.metadata["file_path"]   = doc.metadata.get("file_path", "")
                doc.metadata["loaded_at"]   = datetime.now().isoformat()
                first_line = doc.text.split('\n')[0].strip('#').strip()
                doc.metadata["title"]       = first_line[:100] if first_line else doc.metadata["source_file"]

            all_documents.extend(docs)
            print(f"    ✓ נטענו {len(docs)} מסמכים מ-{tool_name}")

        except Exception as e:
            print(f"    ⚠️  שגיאה ב-{tool_name}: {str(e)}")

    if not all_documents:
        raise ValueError("❌ לא נמצאו מסמכים!")

    print(f"\n📊 סה\"כ נטענו: {len(all_documents)} מסמכים")
    return all_documents


# ===== שלב 2-5: Chunking + Embedding + VectorStoreIndex + Pinecone =====
def initialize_index():
    documents = load_documents()
    print("\n🔧 שלב 2-5 - Chunking + Embedding + Indexing...")

    vector_store = get_vector_store()
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    node_parser = MarkdownNodeParser()
    nodes = node_parser.get_nodes_from_documents(documents)

    for node in nodes:
        header_path = node.metadata.get("header_path")
        if isinstance(header_path, list):
            section_header = " > ".join([h for h in header_path if h])
        else:
            section_header = header_path or ""
        node.metadata["section_header"] = section_header

        if "Slate Gray" in node.get_content():
            print("🧩 נמצא Node עם 'Slate Gray'", {
                "file": node.metadata.get("source_file"),
                "section_header": section_header,
            })

    try:
        index = VectorStoreIndex(
            nodes,
            storage_context=storage_context,
            show_progress=True
        )
    except Exception as e:
        print(f"⚠️  אינדוקס ל-Pinecone נכשל, עובר ל-SimpleVectorStore. סיבה: {str(e)}")
        vector_store = SimpleVectorStore()
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        index = VectorStoreIndex(
            nodes,
            storage_context=storage_context,
            show_progress=True
        )

    print("✅ האינדוקס הושלם!\n")
    return index


index = initialize_index()

# ===== Query Engine =====
print("🔧 מגדיר Query Engine...")

retriever = VectorIndexRetriever(index=index, similarity_top_k=5)
node_postprocessors = [SimilarityPostprocessor(similarity_cutoff=0.1)]
response_synthesizer = get_response_synthesizer(response_mode="compact", use_async=False)

query_engine = RetrieverQueryEngine(
    retriever=retriever,
    node_postprocessors=node_postprocessors,
    response_synthesizer=response_synthesizer
)

print("✅ Query Engine מוכן!\n")


# ===== ממשק Gradio =====
def chat_function(message, history):
    if not message or not message.strip():
        return "נא להזין שאלה."

    print(f"\n🔍 שאלה: {message}")
    try:
        response = query_engine.query(message)
        answer   = str(response)

        if hasattr(response, 'source_nodes') and response.source_nodes:
            answer += "\n\n---\n📚 **מקורות:**\n"
            seen = set()
            for i, node in enumerate(response.source_nodes[:3], 1):
                tool   = node.metadata.get('tool', 'לא ידוע')
                src    = node.metadata.get('source_file', 'לא ידוע')
                title  = node.metadata.get('title', '')
                section = node.metadata.get('section_header', '')
                score  = round(node.score, 3) if node.score else 'N/A'
                key    = f"{tool}:{src}"
                if key not in seen:
                    answer += f"{i}. **{tool}** › {src}"
                    if section:
                        answer += f" (Section: {section})"
                    if title:
                        answer += f" — _{title}_"
                    answer += f" (score: {score})\n"
                    seen.add(key)
        else:
            answer += "\n\n_לא נמצאו מקורות רלוונטיים. נסי לנסח את השאלה אחרת._"

        return answer
    except Exception as e:
        return f"שגיאה: {str(e)}"


demo = gr.ChatInterface(
    fn=chat_function,
    title="🔍 Agentic Docs RAG Explorer",
    description="שאל שאלות על קבצי התיעוד של כלי ה-Agentic Coding בפרויקט שלך.",
    examples=[
        "מה הצבע העיקרי שנבחר לדיזיין?",
        "האם קיימת הנחיה לגבי שימוש ב-RTL?",
        "איזה רכיב הוגדר כרגיש במיוחד?",
        "האם קיימת מגבלה טכנית חוזרת?",
    ]
)

if __name__ == "__main__":
    demo.launch()
