"""
Qdrant Storage — 6-bosqich (Indexing pipeline'ning oxirgi bosqichi)

Qdrant — vector database. U "point"larni saqlaydi. Har bir point uch qismdan iborat:

    id      -> chunk_id (barqaror UUID)
    vector  -> chunk embedding'i, masalan 384 ta son
    payload -> JSON ko'rinishidagi qo'shimcha ma'lumot: chunk matni va metadata
               {"chunk_text": "...", "source": "high_pressing.pdf", "page": 2, ...}

Vector — qidiruv uchun (ma'no bo'yicha yaqinlik).
Payload — natijani tushunish va filter qilish uchun:
  * chunk_text — topilgan chunk'ning o'zi (LLM'ga keyinchalik shu matn beriladi);
  * source / page — citation va provenance;
  * match_id / team_id / player_id — kelajakda "faqat shu o'yin bo'yicha" filter.

Barqaror (stable) ID nima uchun muhim?
    Qdrant'ning upsert amali: shu ID'li point bo'lsa — yangilaydi, bo'lmasa — qo'shadi.
    ID'lar har safar bir xil bo'lgani uchun bitta hujjatni 10 marta ingest qilsak ham,
    Qdrant'da 10 ta nusxa emas, bitta nusxa qoladi (idempotent ingestion).
    Qo'shimcha: hujjat o'zgarib, chunk'lari kamaysa, eski "ortiqcha" chunk'lar qolib ketmasligi
    uchun avval shu document_id'ga tegishli point'larni o'chirib, keyin yangilarini yozamiz.

Input:  Chunk'lar + ularning vector'lari
Output: Qdrant collection'idagi point'lar

Bu modul embedding'lar QANDAY olinganini bilmaydi — u tayyor vector'larni qabul qiladi.
"""

import warnings
from collections import defaultdict
from typing import Optional

import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    FilterSelector,
    MatchValue,
    PayloadSchemaType,
    PointStruct,
    VectorParams,
)

from tactiq.indexing.chunking import Chunk

# Shu payload maydonlari bo'yicha tez filter qilish uchun Qdrant'da index yaratiladi.
INDEXED_PAYLOAD_FIELDS = ["document_id", "source", "document_type", "topic", "language"]


def create_qdrant_client(url: str, api_key: Optional[str] = None, local_path: Optional[str] = None) -> QdrantClient:
    """Qdrant client yaratadi.

    Ikki rejim:
      * Server rejimi (asosiy): Docker'dagi yoki Qdrant Cloud'dagi Qdrant'ga ulanadi (url orqali).
      * Local rejim: local_path berilsa, Qdrant diskdagi papkada, Python ichida ishlaydi.
        Docker o'rnatilmagan kompyuterda o'rganish uchun qulay, lekin production uchun emas.
    """
    if local_path:
        return QdrantClient(path=local_path)
    return QdrantClient(url=url, api_key=api_key)


def build_payload(chunk: Chunk, embedding_model_name: str) -> dict:
    """Bitta chunk uchun Qdrant payload'ini yasaydi.

    Barcha metadata maydonlari saqlanadi; embedding model nomi ham qo'shiladi —
    kelajakda savolni AYNAN shu model bilan embed qilish kerakligini bilish uchun.
    """
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
    """Bitta Qdrant collection bilan ishlash: yaratish, yozish, sanash, ko'rib chiqish.

    Collection — SQL'dagi "jadval"ga o'xshash: bir xil o'lchamdagi vector'lar to'plami.
    """

    def __init__(self, client: QdrantClient, collection_name: str):
        self.client = client
        self.collection_name = collection_name

    def ensure_collection(self, vector_dimension: int) -> bool:
        """Collection bo'lmasa — yaratadi. Bo'lsa — o'lchami mosligini tekshiradi.

        Input:  vector_dimension — EmbeddingModel.dimension (qo'lda yozilmagan, model'dan olingan).
        Output: True — yangi yaratildi; False — avvaldan bor edi.

        Distance.COSINE — vector'lar orasidagi yaqinlik cosine similarity bilan o'lchanadi.
        """
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
        """Payload index — filter'larni tezlashtiradi (kitobdagi mundarija kabi).

        Local rejimda payload index ta'sir qilmaydi va Qdrant client ogohlantirish (warning) chiqaradi.
        `with warnings.catch_warnings():` — context manager: blok ichida warning'larni yashiradi,
        blokdan chiqqach esa avvalgi holat avtomatik tiklanadi.
        """
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            for field_name in INDEXED_PAYLOAD_FIELDS:
                self.client.create_payload_index(self.collection_name, field_name, PayloadSchemaType.KEYWORD)

    def get_vector_dimension(self) -> int:
        info = self.client.get_collection(self.collection_name)
        return info.config.params.vectors.size

    def delete_document(self, document_id: str) -> None:
        """Bitta hujjatga tegishli barcha point'larni o'chiradi (filter: document_id = ...)."""
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
        """Chunk'larni vector va payload bilan Qdrant'ga yozadi.

        Qadamlar:
          1. Shu chunk'lar tegishli bo'lgan hujjatlarning eski point'larini o'chiramiz.
          2. Har bir chunk uchun PointStruct (id + vector + payload) yasaymiz.
          3. Point'larni batch'lar bilan yuboramiz (bitta ulkan so'rov o'rniga bir nechta kichik).

        Output: yozilgan point'lar soni.
        """
        if len(chunks) != len(vectors):
            raise ValueError(f"Chunk'lar soni ({len(chunks)}) va vector'lar soni ({len(vectors)}) teng emas")

        # 1. Eski versiyalarni tozalash
        # defaultdict(list) — mavjud bo'lmagan kalit so'ralganda avtomatik bo'sh ro'yxat yaratadi.
        chunks_by_document = defaultdict(list)
        for chunk in chunks:
            chunks_by_document[chunk.document_id].append(chunk)
        for document_id in chunks_by_document:
            self.delete_document(document_id)

        # 2. Point'larni yasash
        points = []
        # zip(a, b) — ikki ro'yxatni juftlab aylanadi: (chunks[0], vectors[0]), (chunks[1], vectors[1]), ...
        for chunk, vector in zip(chunks, vectors):
            point = PointStruct(
                id=chunk.chunk_id,
                vector=vector.tolist(),  # numpy array -> oddiy Python list (JSON'ga aylantirish uchun)
                payload=build_payload(chunk, embedding_model_name),
            )
            points.append(point)

        # 3. Batch'lar bilan yuborish
        for start in range(0, len(points), batch_size):
            batch = points[start : start + batch_size]
            self.client.upsert(collection_name=self.collection_name, points=batch, wait=True)

        return len(points)

    def count(self) -> int:
        """Collection'dagi jami point'lar soni (exact=True — taxminiy emas, aniq son)."""
        return self.client.count(self.collection_name, exact=True).count

    def peek(self, limit: int = 3) -> list:
        """Collection'dagi bir nechta point'ni ko'rsatadi (tekshirish uchun).

        scroll — hech qanday qidiruvsiz point'larni tartib bilan o'qish. Bu similarity search EMAS.
        """
        points, _next_page = self.client.scroll(
            collection_name=self.collection_name,
            limit=limit,
            with_payload=True,
            with_vectors=False,
        )
        return points
