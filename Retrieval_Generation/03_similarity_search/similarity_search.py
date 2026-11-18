"""
03 — Similarity Search: savol vector'ini Qdrant'dagi chunk vector'lari bilan solishtiradi (cosine).

score 1 ga qancha yaqin — chunk savolga shuncha o'xshash. Natija kattadan kichikka tartiblangan.

    python Retrieval_Generation/03_similarity_search/similarity_search.py

Keyingi bosqich: 04 — Top-k Retrieval
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # Retrieval_Generation/
import rag_paths  # noqa: E402,F401

from qdrant_client import QdrantClient  # noqa: E402  — Qdrant client (pip install qdrant-client)


def similarity_search(
    client: QdrantClient, collection: str, query_vector: list[float], limit: int = 10, query_filter=None
) -> list:
    """Eng o'xshash `limit` ta point'ni (score + payload) qaytaradi. query_filter — ixtiyoriy metadata filter."""
    return client.query_points(
        collection, query=query_vector, limit=limit, with_payload=True, query_filter=query_filter
    ).points


if __name__ == "__main__":
    from config.settings import get_settings
    from embedding_model import EmbeddingModel
    from query_embedding import embed_question
    from user_question import SAMPLE_QUESTIONS
    from vector_database import create_qdrant_client

    settings = get_settings()
    model = EmbeddingModel(settings.embedding_model_name)
    client = create_qdrant_client(settings.qdrant_url, settings.qdrant_api_key, settings.qdrant_local_path)

    question = SAMPLE_QUESTIONS[0]
    points = similarity_search(client, settings.qdrant_collection, embed_question(question, model))
    print(f"Savol: {question}\n")
    for point in points:
        print(f"  score={point.score:.3f}  {point.payload['source']} (page={point.payload['page']})")
    client.close()
