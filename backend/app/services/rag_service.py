from google import genai
from google.genai import types
import chromadb

from app.config import settings

_collection = None
_genai_client = None


def _chunk_text(text: str, size: int = 500, overlap: int = 50) -> list[str]:
    chunks = []
    start = 0
    while start < len(text):
        chunks.append(text[start : start + size])
        start += size - overlap
    return [c for c in chunks if c.strip()]


def _embed(text: str, task_type: str) -> list[float]:
    result = _genai_client.models.embed_content(
        model="gemini-embedding-001",
        contents=text,
        config=types.EmbedContentConfig(task_type=task_type),
    )
    return result.embeddings[0].values


def initialize(policy_file: str) -> None:
    global _collection, _genai_client
    try:
        _genai_client = genai.Client(api_key=settings.GEMINI_API_KEY)
        client = chromadb.Client()
        _collection = client.create_collection("policy")

        with open(policy_file, "r", encoding="utf-8") as f:
            text = f.read()

        chunks = _chunk_text(text)
        for i, chunk in enumerate(chunks):
            embedding = _embed(chunk, "RETRIEVAL_DOCUMENT")
            _collection.add(
                documents=[chunk],
                embeddings=[embedding],
                ids=[f"chunk_{i}"],
            )
        print(f"RAG başlatıldı: {len(chunks)} chunk yüklendi.")
    except Exception as e:
        _collection = None
        print(f"RAG init başarısız: {e}")


def search(query: str, n_results: int = 3) -> str:
    if _collection is None:
        return "Politika bilgisine erişilemiyor."
    try:
        embedding = _embed(query, "RETRIEVAL_QUERY")
        results = _collection.query(
            query_embeddings=[embedding],
            n_results=min(n_results, _collection.count()),
        )
        return "\n\n".join(results["documents"][0])
    except Exception as e:
        return f"Politika araması başarısız: {e}"
