"""
שלב ג' — Data Extraction + Router
LLM: Cohere command-r-08-2024 (ללא OpenAI)
"""

import os
import ssl
import warnings
import urllib3
import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Optional
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

from llama_index.core import SimpleDirectoryReader, Settings, VectorStoreIndex, StorageContext
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.postprocessor import SimilarityPostprocessor
from llama_index.core.response_synthesizers import get_response_synthesizer
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.embeddings.cohere import CohereEmbedding
from llama_index.llms.cohere import Cohere
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.core.program import LLMTextCompletionProgram
from pydantic import BaseModel, Field
from pinecone import Pinecone
import gradio as gr

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

KNOWLEDGE_DB_PATH = "./knowledge_db.json"


# ===== סכמה =====
class Decision(BaseModel):
    id: str = Field(description="מזהה ייחודי, למשל dec-001")
    title: str = Field(description="כותרת קצרה")
    summary: str = Field(description="תיאור קצר")
    tags: list[str] = Field(default=[])

class Rule(BaseModel):
    id: str = Field(description="מזהה ייחודי, למשל rule-001")
    rule: str = Field(description="ניסוח הכלל")
    scope: str = Field(description="תחום: ui, api, db, general")
    notes: Optional[str] = Field(default=None)

class Warning(BaseModel):
    id: str = Field(description="מזהה ייחודי, למשל warn-001")
    area: str = Field(description="האזור הרגיש")
    message: str = Field(description="תיאור האזהרה")
    severity: str = Field(description="high, medium, low")

class Dependency(BaseModel):
    id: str = Field(description="מזהה ייחודי, למשל dep-001")
    name: str = Field(description="שם התלות")
    reason: str = Field(description="למה חשובה")
    version: Optional[str] = Field(default=None)

class ExtractedItems(BaseModel):
    decisions:    list[Decision]   = Field(default=[])
    rules:        list[Rule]       = Field(default=[])
    warnings:     list[Warning]    = Field(default=[])
    dependencies: list[Dependency] = Field(default=[])


# ===== Data Extraction =====
def extract_from_document(text: str, tool: str, file_path: str, observed_at: str) -> dict:
    prompt = f"""
אתה מנתח מסמכי תיעוד של פרויקטי תוכנה.
קרא את המסמך וחלץ:
1. decisions — החלטות טכניות/ארכיטקטורה
2. rules — כללים/הנחיות שחייבים לעמוד בהן
3. warnings — אזהרות/רגישויות שלא לשבור
4. dependencies — ספריות/שירותים חיצוניים קריטיים

אם לא קיים פריט מסוג מסוים — החזר רשימה ריקה.
צור מזהים בפורמט: dec-001, rule-001, warn-001, dep-001

מסמך:
---
{text[:3000]}
---
"""
    try:
        program = LLMTextCompletionProgram.from_defaults(
            output_cls=ExtractedItems,
            prompt_template_str=prompt,
            llm=Settings.llm,
            verbose=False
        )
        result = program()

        def add_source(items):
            out = []
            for item in items:
                d = item.model_dump()
                d["source"]      = {"tool": tool, "file": file_path}
                d["observed_at"] = observed_at
                out.append(d)
            return out

        return {
            "decisions":    add_source(result.decisions),
            "rules":        add_source(result.rules),
            "warnings":     add_source(result.warnings),
            "dependencies": add_source(result.dependencies),
        }
    except Exception as e:
        print(f"    ⚠️  שגיאה בחילוץ: {str(e)}")
        return {"decisions": [], "rules": [], "warnings": [], "dependencies": []}


def build_knowledge_db() -> dict:
    tools_paths = {
        "cursor":      "./.cursor",
        "claude_code": "./.claude",
        "windsurf":    "./.windsurf",
        "kiro":        "./.kiro",
        "docs_ai":     "./docs_ai"
    }

    knowledge_db = {
        "schema_version": "1.0",
        "generated_at":   datetime.now().isoformat(),
        "sources":        [],
        "items":          {"decisions": [], "rules": [], "warnings": [], "dependencies": []}
    }

    counters = {"dec": 1, "rule": 1, "warn": 1, "dep": 1}
    prefixes = {"decisions": "dec", "rules": "rule", "warnings": "warn", "dependencies": "dep"}

    for tool_name, tool_path in tools_paths.items():
        if not os.path.exists(tool_path):
            continue

        print(f"  📂 מחלץ מ-{tool_name}...")
        files_info = []

        try:
            docs = SimpleDirectoryReader(input_dir=tool_path, recursive=True, required_exts=[".md"]).load_data()
        except Exception as e:
            print(f"    ⚠️  {e}")
            continue

        for doc in docs:
            file_path   = doc.metadata.get("file_path", "")
            file_name   = doc.metadata.get("file_name", "")
            observed_at = datetime.now().isoformat()
            file_hash   = "sha256:" + hashlib.sha256(doc.text.encode()).hexdigest()[:16]

            files_info.append({"path": file_path, "last_modified": observed_at, "hash": file_hash})
            print(f"    📄 מחלץ מ-{file_name}...")

            extracted = extract_from_document(doc.text, tool_name, file_path, observed_at)

            for category, prefix in prefixes.items():
                for item in extracted[category]:
                    item["id"] = f"{prefix}-{counters[prefix]:03d}"
                    counters[prefix] += 1
                    knowledge_db["items"][category].append(item)

        knowledge_db["sources"].append({"tool": tool_name, "root_path": tool_path, "files": files_info})

    with open(KNOWLEDGE_DB_PATH, "w", encoding="utf-8") as f:
        json.dump(knowledge_db, f, ensure_ascii=False, indent=2)

    total = sum(len(knowledge_db["items"][k]) for k in knowledge_db["items"])
    print(f"\n✅ knowledge_db.json נשמר — {total} פריטים חולצו")
    return knowledge_db


def load_knowledge_db() -> dict:
    if os.path.exists(KNOWLEDGE_DB_PATH):
        with open(KNOWLEDGE_DB_PATH, "r", encoding="utf-8") as f:
            db = json.load(f)
        total = sum(len(db["items"][k]) for k in db["items"])
        print(f"✅ נטען knowledge_db.json — {total} פריטים")
        return db
    print("📦 בונה knowledge_db.json לראשונה...")
    return build_knowledge_db()


# ===== Router =====
def decide_route(query: str) -> str:
    prompt = f"""
אתה מערכת ניתוב. בחר בין שני מצבים:
- "semantic": לשאלות כלליות, הסברים, "איך", "מה זה"
- "structured": לשאלות שדורשות רשימה מלאה, עדכניות, סינון לפי זמן, או סוג ספציפי (החלטות/אזהרות/כללים)

השב במילה אחת: semantic או structured.

שאלה: {query}
"""
    response = Settings.llm.complete(prompt)
    route = response.text.strip().lower()
    return "structured" if "structured" in route else "semantic"


def query_structured(query: str, knowledge_db: dict) -> str:
    db_str = json.dumps(knowledge_db["items"], ensure_ascii=False, indent=2)
    prompt = f"""
יש לך מאגר נתונים JSON של פרויקט תוכנה עם: decisions, rules, warnings, dependencies.
ענה על השאלה בהתבסס על הנתונים בלבד. אם אין מידע — אמור זאת.

שאלה: {query}

מאגר:
{db_str[:4000]}
"""
    response = Settings.llm.complete(prompt)
    return response.text.strip()


def query_semantic(query: str) -> str:
    retriever    = VectorIndexRetriever(index=index, similarity_top_k=5)
    postprocessor = SimilarityPostprocessor(similarity_cutoff=0.5)
    synthesizer  = get_response_synthesizer(response_mode="compact")
    query_engine = RetrieverQueryEngine(
        retriever=retriever,
        node_postprocessors=[postprocessor],
        response_synthesizer=synthesizer
    )
    response = query_engine.query(query)
    answer   = str(response)

    if hasattr(response, 'source_nodes') and response.source_nodes:
        answer += "\n\n---\n📚 **מקורות:**\n"
        seen = set()
        for i, node in enumerate(response.source_nodes[:3], 1):
            tool  = node.metadata.get('tool', 'לא ידוע')
            src   = node.metadata.get('source_file', 'לא ידוע')
            score = round(node.score, 3) if node.score else 'N/A'
            key   = f"{tool}:{src}"
            if key not in seen:
                answer += f"{i}. **{tool}** › {src} (score: {score})\n"
                seen.add(key)
    return answer


# ===== אתחול =====
print("\n📦 טוען/בונה מאגר נתונים מובנה...")
knowledge_db = load_knowledge_db()


# ===== Gradio עם Router =====
def chat_with_router(message, history):
    if not message or not message.strip():
        return "נא להזין שאלה."

    print(f"\n🔀 [Router] שאלה: '{message}'")
    route = decide_route(message)
    print(f"   ניתוב: {route}")

    if route == "structured":
        answer = query_structured(message, knowledge_db)
        return f"🗂️ **[שליפה מובנית]**\n\n{answer}"
    else:
        answer = query_semantic(message)
        return f"🔍 **[חיפוש סמנטי]**\n\n{answer}"


demo = gr.ChatInterface(
    fn=chat_with_router,
    title="🔍 Agentic Docs RAG — Data Extraction + Router",
    description=(
        "שלב ג': Router מחליט אוטומטית בין חיפוש סמנטי לשליפה מובנית.\n\n"
        "**שליפה מובנית:** 'תן לי את כל ההחלטות', 'אילו אזהרות קיימות'\n"
        "**חיפוש סמנטי:** 'מה הצבע שנבחר לדיזיין', 'איך מתקינים'"
    ),
    examples=[
        "תן לי רשימה של כל ההחלטות הטכניות",
        "אילו אזהרות קיימות במערכת?",
        "מה הצבע העיקרי שנבחר לדיזיין?",
        "האם קיימת הנחיה לגבי שימוש ב-RTL?",
        "אילו תלויות טכניות קריטיות קיימות?",
    ]
)

if __name__ == "__main__":
    import sys
    if "--rebuild" in sys.argv:
        print("🔄 בונה מחדש את knowledge_db.json...")
        build_knowledge_db()
    demo.launch()
