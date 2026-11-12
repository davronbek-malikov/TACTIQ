"""
04 — Top-k Retrieval: eng mos k ta chunk'ni tanlaydi.

min_score'dan past chunk'lar tashlanadi — ular savolga aloqador emas.
Hech biri qolmasa, LLM chaqirilmaydi (javobni o'ylab topmaslik uchun).

    python Retrieval_Generation/04_top_k_retrieval/top_k_retrieval.py

Keyingi bosqich: 05 — Prompt Construction
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class RetrievedChunk:
    text: str
    source: str
    page: Optional[int]
    score: float


def select_top_k(points: list, k: int = 3, min_score: float = 0.3) -> list[RetrievedChunk]:
    """Score bo'yicha eng yaxshi k ta chunk (points allaqachon kattadan kichikka tartiblangan)."""
    chunks = []
    for point in points[:k]:
        if point.score < min_score:
            break
        chunks.append(
            RetrievedChunk(
                text=point.payload["chunk_text"],
                source=point.payload["source"],
                page=point.payload["page"],
                score=point.score,
            )
        )
    return chunks


if __name__ == "__main__":
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    import rag_paths  # noqa: F401
    from config.settings import get_settings
    from embedding_model import EmbeddingModel
    from query_embedding import embed_question
    from similarity_search import similarity_search
    from user_question import SAMPLE_QUESTIONS
    from vector_database import create_qdrant_client

    settings = get_settings()
    model = EmbeddingModel(settings.embedding_model_name)
    client = create_qdrant_client(settings.qdrant_url, settings.qdrant_api_key, settings.qdrant_local_path)

    for question in SAMPLE_QUESTIONS:
        points = similarity_search(client, settings.qdrant_collection, embed_question(question, model))
        chunks = select_top_k(points)
        print(f"\nSavol: {question}  ->  {len(chunks)} ta chunk")
        for chunk in chunks:
            print(f"  score={chunk.score:.3f}  {chunk.source} (page={chunk.page})")
    client.close()
