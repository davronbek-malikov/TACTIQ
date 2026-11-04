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

import warnings  # warnings — ogohlantirishlar (warning) bilan ishlash standart kutubxonasi
from collections import defaultdict  # defaultdict — kalit bo'lmasa avtomatik default qiymat yaratadigan dict
from typing import Optional  # Optional[str] — "str yoki None"

import numpy as np  # numpy — vector'lar numpy array ko'rinishida keladi (type hint uchun kerak)
from qdrant_client import QdrantClient  # qdrant-client — Qdrant bilan Python orqali gaplashish kutubxonasi.
#                                         QdrantClient — Qdrant server'ga (yoki local papkaga) ulanish obyekti.
from qdrant_client.models import (  # models — Qdrant so'rovlari uchun tayyor ma'lumot tuzilmalari:
    Distance,           # vector'lar orasidagi masofa turi (COSINE, DOT, EUCLID)
    FieldCondition,     # filter sharti: "payload'dagi shu maydon ..."
    Filter,             # bir yoki bir nechta shartdan iborat filter
    FilterSelector,     # "filter'ga mos point'larni tanla" (o'chirish uchun)
    MatchValue,         # "maydon qiymati aynan shunga teng bo'lsin"
    PayloadSchemaType,  # payload index turi (KEYWORD — aniq matn qiymati)
    PointStruct,        # bitta point: id + vector + payload
    VectorParams,       # collection sozlamasi: vector o'lchami va masofa turi
)

from indexing.step4_chunking import Chunk  # 4-bosqichdagi Chunk dataclass

# Shu payload maydonlari bo'yicha tez filter qilish uchun Qdrant'da index yaratiladi.
INDEXED_PAYLOAD_FIELDS = ["document_id", "source", "document_type", "topic", "language"]


def create_qdrant_client(url: str, api_key: Optional[str] = None, local_path: Optional[str] = None) -> QdrantClient:
    """Qdrant client yaratadi.

    Ikki rejim:
      * Server rejimi (asosiy): Docker'dagi yoki Qdrant Cloud'dagi Qdrant'ga ulanadi (url orqali).
      * Local rejim: local_path berilsa, Qdrant diskdagi papkada, Python ichida ishlaydi.
        Docker o'rnatilmagan kompyuterda o'rganish uchun qulay, lekin production uchun emas.
    """
    if local_path:  # local_path None yoki "" bo'lmasa
        return QdrantClient(path=local_path)
    return QdrantClient(url=url, api_key=api_key)  # masalan url="http://localhost:6333"


def build_payload(chunk: Chunk, embedding_model_name: str) -> dict:
    """Bitta chunk uchun Qdrant payload'ini yasaydi.

    Barcha metadata maydonlari saqlanadi; embedding model nomi ham qo'shiladi —
    kelajakda savolni AYNAN shu model bilan embed qilish kerakligini bilish uchun.
    """
    metadata = chunk.metadata
    return {  # .get(...) — kalit bo'lmasa xato emas, None qaytaradi (payload'da bo'sh maydon bo'lib qoladi)
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

    Nima uchun oddiy class (dataclass emas)? Bu class ma'lumot saqlash uchun emas,
    Qdrant bilan ISHLASH uchun: uning asosiy qismi — metodlar (ensure_collection, upsert_chunks ...).
    """

    def __init__(self, client: QdrantClient, collection_name: str):
        self.client = client                    # tayyor ulanish (tashqaridan beriladi — test'da ":memory:" berish oson)
        self.collection_name = collection_name  # masalan "tactiq_documents"

    def ensure_collection(self, vector_dimension: int) -> bool:
        """Collection bo'lmasa — yaratadi. Bo'lsa — o'lchami mosligini tekshiradi.

        Input:  vector_dimension — EmbeddingModel.dimension (qo'lda yozilmagan, model'dan olingan).
        Output: True — yangi yaratildi; False — avvaldan bor edi.
        """
        if self.client.collection_exists(self.collection_name):  # Qdrant'dan so'raymiz: bu collection bormi?
            existing_dimension = self.get_vector_dimension()
            if existing_dimension != vector_dimension:  # "!=" — teng emas
                raise ValueError(
                    f"Collection '{self.collection_name}' {existing_dimension}-o'lchamli, "
                    f"model esa {vector_dimension}-o'lchamli vector beradi. Boshqa embedding model "
                    f"uchun boshqa collection nomini ishlating yoki eskisini o'chiring."
                )
            return False

        self.client.create_collection(  # yangi collection yaratish
            collection_name=self.collection_name,
            # size — vector o'lchami (384); Distance.COSINE — yaqinlik cosine similarity bilan o'lchanadi.
            vectors_config=VectorParams(size=vector_dimension, distance=Distance.COSINE),
        )
        self._create_payload_indexes()
        return True

    def _create_payload_indexes(self) -> None:
        """Payload index — filter'larni tezlashtiradi (kitobdagi mundarija kabi).

        Local rejimda payload index ta'sir qilmaydi va Qdrant client ogohlantirish (warning) chiqaradi.
        """
        # `with warnings.catch_warnings():` — context manager: blok ichida warning'larni yashiradi,
        # blokdan chiqqach esa avvalgi holat avtomatik tiklanadi.
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)  # UserWarning turidagi ogohlantirishlarni e'tiborsiz qoldir
            for field_name in INDEXED_PAYLOAD_FIELDS:
                # KEYWORD — aniq qiymat bo'yicha filter uchun index ("topic = high_pressing")
                self.client.create_payload_index(self.collection_name, field_name, PayloadSchemaType.KEYWORD)

    def get_vector_dimension(self) -> int:
        """Mavjud collection'ning vector o'lchamini Qdrant'dan o'qiydi."""
        info = self.client.get_collection(self.collection_name)  # collection haqidagi to'liq ma'lumot
        return info.config.params.vectors.size  # ichma-ich obyektlardan o'lchamni olamiz

    def delete_document(self, document_id: str) -> None:
        """Bitta hujjatga tegishli barcha point'larni o'chiradi (filter: document_id = ...)."""
        # Filter(must=[...]) — "quyidagi shartlarning HAMMASI bajarilsin" (SQL'dagi WHERE ga o'xshash)
        document_filter = Filter(must=[FieldCondition(key="document_id", match=MatchValue(value=document_id))])
        self.client.delete(
            collection_name=self.collection_name,
            points_selector=FilterSelector(filter=document_filter),  # filter'ga mos barcha point'lar o'chiriladi
        )

    def upsert_chunks(
        self,
        chunks: list[Chunk],
        vectors: np.ndarray,
        embedding_model_name: str,
        batch_size: int = 64,
    ) -> int:
        """Chunk'larni vector va payload bilan Qdrant'ga yozadi.

        upsert = update + insert: shu ID bo'lsa — yangilaydi, bo'lmasa — qo'shadi.

        Qadamlar:
          1. Shu chunk'lar tegishli bo'lgan hujjatlarning eski point'larini o'chiramiz.
          2. Har bir chunk uchun PointStruct (id + vector + payload) yasaymiz.
          3. Point'larni batch'lar bilan yuboramiz (bitta ulkan so'rov o'rniga bir nechta kichik).

        Output: yozilgan point'lar soni.
        """
        if len(chunks) != len(vectors):  # har bir chunk'ga aynan bitta vector to'g'ri kelishi shart
            raise ValueError(f"Chunk'lar soni ({len(chunks)}) va vector'lar soni ({len(vectors)}) teng emas")

        # 1. Eski versiyalarni tozalash
        # defaultdict(list) — mavjud bo'lmagan kalit so'ralganda avtomatik bo'sh ro'yxat yaratadi.
        chunks_by_document = defaultdict(list)
        for chunk in chunks:
            chunks_by_document[chunk.document_id].append(chunk)  # chunk'larni hujjat bo'yicha guruhlaymiz
        for document_id in chunks_by_document:  # dict ustida sikl — kalitlar (document_id'lar) bo'yicha
            self.delete_document(document_id)

        # 2. Point'larni yasash
        points = []
        # zip(a, b) — ikki ro'yxatni juftlab aylanadi: (chunks[0], vectors[0]), (chunks[1], vectors[1]), ...
        for chunk, vector in zip(chunks, vectors):
            point = PointStruct(
                id=chunk.chunk_id,          # barqaror UUID — qayta yozilganda dublikat bo'lmaydi
                vector=vector.tolist(),     # .tolist() — numpy array -> oddiy Python list (Qdrant'ga yuborish uchun)
                payload=build_payload(chunk, embedding_model_name),
            )
            points.append(point)

        # 3. Batch'lar bilan yuborish
        for start in range(0, len(points), batch_size):
            batch = points[start : start + batch_size]
            # wait=True — Qdrant yozib bo'lguncha kutamiz; shunda keyingi count() aniq natija beradi
            self.client.upsert(collection_name=self.collection_name, points=batch, wait=True)

        return len(points)

    def count(self) -> int:
        """Collection'dagi jami point'lar soni (exact=True — taxminiy emas, aniq son)."""
        return self.client.count(self.collection_name, exact=True).count

    def peek(self, limit: int = 3) -> list:
        """Collection'dagi bir nechta point'ni ko'rsatadi (tekshirish uchun).

        scroll — hech qanday qidiruvsiz point'larni tartib bilan o'qish. Bu similarity search EMAS.
        """
        # scroll() ikki qiymat qaytaradi: (point'lar, keyingi_sahifa_belgisi).
        # "_next_page" — "_" bilan boshlangan nom: "bu qiymat bizga kerak emas" degan kelishuv.
        points, _next_page = self.client.scroll(
            collection_name=self.collection_name,
            limit=limit,          # nechta point o'qish
            with_payload=True,    # payload ham kelsin
            with_vectors=False,   # vector'lar kerak emas (384 ta son — ekranda o'qib bo'lmaydi)
        )
        return points
