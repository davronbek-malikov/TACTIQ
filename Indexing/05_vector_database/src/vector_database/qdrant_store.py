"""
05 — Vector Database: chunk'larni Qdrant'ga saqlaydi.

Har bir point = id (chunk_id) + vector (384 son) + payload (chunk matni va metadata).
Barqaror ID + upsert: qayta index qilganda dublikat bo'lmaydi.

Indexing pipeline'ning oxirgi bosqichi.
"""

import warnings
from collections import defaultdict
from typing import Optional

import numpy as np
from qdrant_client import QdrantClient   # Qdrant bilan Python orqali ishlash
from qdrant_client.models import (
    Distance,           # masofa turi (COSINE)
    FieldCondition,     # filter sharti
    Filter,             # filter
    FilterSelector,     # filter'ga mos point'larni tanlash (o'chirish uchun)
    MatchValue,         # "qiymat aynan shunga teng"
    PayloadSchemaType,  # payload index turi
    PointStruct,        # bitta point: id + vector + payload
    VectorParams,       # collection sozlamasi: o'lcham + masofa
)

from chunking import Chunk

# Shu maydonlar bo'yicha filter tez ishlashi uchun index yaratiladi
INDEXED_PAYLOAD_FIELDS = ["document_id", "source", "document_type", "topic", "language"]


def create_qdrant_client(url: str, api_key: Optional[str] = None, local_path: Optional[str] = None) -> QdrantClient:
    """Qdrant'ga ulanish: server (Docker/Cloud) yoki local_path berilsa — diskdagi papka."""
    if local_path:
        return QdrantClient(path=local_path)
    return QdrantClient(url=url, api_key=api_key)


def build_payload(chunk: Chunk, embedding_model_name: str) -> dict:
    """Chunk matni + barcha metadata + model nomi (savolni ham shu model bilan embed qilish uchun)."""
    metadata = chunk.metadata
    return {
        "chunk_id": chunk.chunk_id,
        "document_id": chunk.document_id,
        "chunk_text": chunk.text,
        "source": metadata.get("source"),
        "source_path": metadata.get("source_path"),
        "file_type": metadata.get("file_type"),
        "document_type": metadata.get("document_type"),
        "topic": metadata.get("topic"),
        "language": metadata.get("language"),
        "match_id": metadata.get("match_id"),
        "team_id": metadata.get("team_id"),
        "player_id": metadata.get("player_id"),
        "page": metadata.get("page"),
        "chunk_index": metadata.get("chunk_index"),
        "token_count": metadata.get("token_count"),
        "embedding_model": embedding_model_name,
    }


class QdrantStore:
    """Bitta collection bilan ishlash: yaratish, yozish, sanash, ko'rish."""

    def __init__(self, client: QdrantClient, collection_name: str):
        self.client = client
        self.collection_name = collection_name

    def ensure_collection(self, vector_dimension: int) -> bool:
        """Collection yo'q bo'lsa yaratadi (True). Bor bo'lsa o'lchamini tekshiradi (False)."""
        if self.client.collection_exists(self.collection_name):
            existing_dimension = self.get_vector_dimension()
            if existing_dimension != vector_dimension:
                raise ValueError(
                    f"Collection '{self.collection_name}' {existing_dimension}-o'lchamli, "
                    f"model esa {vector_dimension}-o'lchamli vector beradi. Boshqa embedding model "
                    f"uchun boshqa collection nomini ishlating yoki eskisini o'chiring."
                )
            return False

        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(size=vector_dimension, distance=Distance.COSINE),
        )
        self._create_payload_indexes()
        return True

    def _create_payload_indexes(self) -> None:
        """Filter'larni tezlashtiradigan index'lar (local rejimdagi warning yashiriladi)."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            for field_name in INDEXED_PAYLOAD_FIELDS:
                self.client.create_payload_index(self.collection_name, field_name, PayloadSchemaType.KEYWORD)

    def get_vector_dimension(self) -> int:
        """Collection'ning vector o'lchami."""
        info = self.client.get_collection(self.collection_name)
        return info.config.params.vectors.size

    def delete_document(self, document_id: str) -> None:
        """Bitta hujjatning barcha point'larini o'chiradi."""
        document_filter = Filter(must=[FieldCondition(key="document_id", match=MatchValue(value=document_id))])
        self.client.delete(
            collection_name=self.collection_name,
            points_selector=FilterSelector(filter=document_filter),
        )

    def upsert_chunks(
        self,
        chunks: list[Chunk],
        vectors: np.ndarray,
        embedding_model_name: str,
        batch_size: int = 64,
    ) -> int:
        """Chunk'larni Qdrant'ga yozadi va yozilganlar sonini qaytaradi.

        1. Hujjatning eski point'larini o'chiramiz (hujjat qisqargan bo'lsa ortiqchasi qolmasin).
        2. Har bir chunk -> PointStruct (id + vector + payload).
        3. Batch'lar bilan yuboramiz. upsert = bor bo'lsa yangilaydi, yo'q bo'lsa qo'shadi.
        """
        if len(chunks) != len(vectors):
            raise ValueError(f"Chunk'lar soni ({len(chunks)}) va vector'lar soni ({len(vectors)}) teng emas")

        chunks_by_document = defaultdict(list)
        for chunk in chunks:
            chunks_by_document[chunk.document_id].append(chunk)
        for document_id in chunks_by_document:
            self.delete_document(document_id)

        points = []
        for chunk, vector in zip(chunks, vectors):
            point = PointStruct(
                id=chunk.chunk_id,
                vector=vector.tolist(),  # numpy -> oddiy list
                payload=build_payload(chunk, embedding_model_name),
            )
            points.append(point)

        for start in range(0, len(points), batch_size):
            batch = points[start : start + batch_size]
            self.client.upsert(collection_name=self.collection_name, points=batch, wait=True)

        return len(points)

    def count(self) -> int:
        """Collection'dagi point'lar soni."""
        return self.client.count(self.collection_name, exact=True).count

    def peek(self, limit: int = 3) -> list:
        """Bir nechta point'ni ko'rsatadi (qidiruv emas — oddiy o'qish)."""
        points, _next_page = self.client.scroll(
            collection_name=self.collection_name,
            limit=limit,
            with_payload=True,
            with_vectors=False,
        )
        return points
