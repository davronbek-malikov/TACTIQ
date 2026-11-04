"""4-bosqich: Storing — vector + payload (matn va metadata)ni Qdrant'ga yozish.

Qdrant'da bitta "point" = id + vector + payload.
  id      -> chunk.id (deterministic UUID, qayta index qilsak dublikat bo'lmaydi)
  vector  -> embedding (1024 son)
  payload -> {"text": ..., "source": ..., "page": ..., "department": ...}
"""

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PayloadSchemaType, PointStruct, VectorParams

from config import QDRANT_API_KEY, QDRANT_LOCAL_PATH, QDRANT_URL
from indexing_pipeline.chunking import Chunk

# Shu maydonlar bo'yicha tez filter qilish uchun payload index yaratamiz
FILTERABLE_FIELDS = ["department", "file_type", "language", "source"]


def get_client() -> QdrantClient:
    """QDRANT_URL bo'lsa server (Docker / Qdrant Cloud), bo'lmasa local mode (papka)."""
    if QDRANT_URL:
        return QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
    return QdrantClient(path=str(QDRANT_LOCAL_PATH))


def create_collection(client: QdrantClient, name: str, dimension: int, recreate: bool = False) -> None:
    if client.collection_exists(name):
        if not recreate:
            return
        client.delete_collection(name)

    client.create_collection(
        collection_name=name,
        vectors_config=VectorParams(size=dimension, distance=Distance.COSINE),
    )
    if QDRANT_URL:  # local mode payload index'ni qo'llab-quvvatlamaydi (u yerda baribir tez)
        for field_name in FILTERABLE_FIELDS:
            client.create_payload_index(name, field_name, PayloadSchemaType.KEYWORD)


def upsert_chunks(
    client: QdrantClient,
    name: str,
    chunks: list[Chunk],
    vectors,
    batch_size: int = 64,
) -> None:
    """upsert = bor bo'lsa yangilaydi, yo'q bo'lsa qo'shadi."""
    points = [
        PointStruct(id=chunk.id, vector=vector.tolist(), payload={"text": chunk.text, **chunk.metadata})
        for chunk, vector in zip(chunks, vectors, strict=True)
    ]
    for start in range(0, len(points), batch_size):
        client.upsert(collection_name=name, points=points[start : start + batch_size])
