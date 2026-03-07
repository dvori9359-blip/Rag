"""
Local indexing and retrieval test using SimpleVectorStore (no Pinecone).
Creates local_index/index.json and runs a direct query for PostgreSQL.
"""

import os
from datetime import datetime
from dotenv import load_dotenv

from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, StorageContext, Settings
from llama_index.core.node_parser import MarkdownNodeParser
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.postprocessor import SimilarityPostprocessor
from llama_index.core.vector_stores import SimpleVectorStore
from llama_index.embeddings.cohere import CohereEmbedding
from llama_index.llms.cohere import Cohere

load_dotenv()

COHERE_API_KEY = os.getenv("COHERE_API_KEY")
if not COHERE_API_KEY:
    raise ValueError("נא לוודא COHERE_API_KEY ב-.env")

Settings.embed_model = CohereEmbedding(api_key=COHERE_API_KEY, model_name="embed-multilingual-v3.0")
Settings.llm = Cohere(api_key=COHERE_API_KEY, model="command-r-08-2024")


def load_documents():
    base_dir = os.path.abspath(os.getcwd())
    tools_paths = {
        "cursor": os.path.join(base_dir, ".cursor"),
        "claude_code": os.path.join(base_dir, ".claude"),
        "windsurf": os.path.join(base_dir, ".windsurf"),
        "kiro": os.path.join(base_dir, ".kiro"),
        "docs_ai": os.path.join(base_dir, "docs_ai"),
    }

    all_documents = []
    from pathlib import Path

    for tool_name, tool_path in tools_paths.items():
        if not os.path.exists(tool_path):
            continue

        md_files = [str(p) for p in Path(tool_path).rglob("*.md")]
        if not md_files:
            continue

        docs = SimpleDirectoryReader(input_files=md_files).load_data()
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
    index = VectorStoreIndex(nodes, storage_context=storage_context, show_progress=True)

    os.makedirs("local_index", exist_ok=True)
    storage_context.persist(persist_dir="local_index")

    # Create a simple index.json snapshot for inspection
    with open("local_index/index.json", "w", encoding="utf-8") as f:
        import json
        json.dump(
            [
                {
                    "id": n.node_id,
                    "tool": n.metadata.get("tool"),
                    "file_path": n.metadata.get("file_path"),
                    "section_header": n.metadata.get("section_header"),
                }
                for n in nodes
            ],
            f,
            ensure_ascii=False,
            indent=2,
        )

    return index


def dry_run_query(index, query: str):
    retriever = VectorIndexRetriever(index=index, similarity_top_k=5)
    postprocessor = SimilarityPostprocessor(similarity_cutoff=0.1)
    nodes = retriever.retrieve(query)
    nodes = postprocessor.postprocess_nodes(nodes)

    print("\n🔎 Query:", query)
    print("\n✅ Retrieved Nodes:")
    for node in nodes[:3]:
        print(
            {
                "tool": node.metadata.get("tool"),
                "file": node.metadata.get("source_file"),
                "section_header": node.metadata.get("section_header"),
                "text_preview": node.get_content()[:120],
            }
        )


if __name__ == "__main__":
    index = build_local_index()
    dry_run_query(index, "PostgreSQL")
