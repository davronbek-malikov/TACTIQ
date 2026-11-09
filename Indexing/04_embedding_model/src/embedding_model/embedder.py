"""
04 — Embedding Model: har bir chunk matnini vector'ga (384 ta son) aylantiradi.

Ma'nosi yaqin matnlar -> yaqin vector'lar. Shu keyinchalik qidiruvning asosi.
Hujjatlar va savollar BIR XIL model bilan embed qilinishi shart.

Keyingi bosqich: 05 — Vector Database
"""

import numpy as np                                     # vector'lar bilan hisob-kitob
from sentence_transformers import SentenceTransformer  # Hugging Face embedding modellari


class EmbeddingModel:
    """Modelni bir marta yuklaydi va qayta-qayta ishlatadi.

    Oddiy class (dataclass emas): __init__ ish bajaradi — modelni yuklaydi va o'lchamni hisoblaydi.
    """

    def __init__(self, model_name: str, batch_size: int = 32):
        self.model_name = model_name
        self.batch_size = batch_size
        self.model = SentenceTransformer(model_name)  # birinchi marta internetdan, keyin keshdan

        # O'lchamni qo'lda yozmaymiz — model natijasidan olamiz (MiniLM uchun 384)
        test_vector = self.model.encode(["dimension check"], normalize_embeddings=True)
        self.dimension = int(test_vector.shape[1])

    @property
    def max_seq_length(self) -> int:
        """Model ko'ra oladigan maksimal token soni (MiniLM — 256). Undan uzun qism kesiladi."""
        return int(self.model.max_seq_length)

    def embed(self, texts: list[str]) -> np.ndarray:
        """Matnlar -> vector'lar, shakli (matnlar soni, dimension).

        Batch: matnlar 32 tadan guruhlab yuboriladi — tezroq va xotira to'lmaydi.
        normalize: har bir vector uzunligi 1 — shunda cosine similarity = dot product.
        """
        if len(texts) == 0:
            return np.zeros((0, self.dimension), dtype=np.float32)

        batches = []
        total_batches = (len(texts) + self.batch_size - 1) // self.batch_size
        for batch_number, start in enumerate(range(0, len(texts), self.batch_size), start=1):
            batch_texts = texts[start : start + self.batch_size]
            batch_vectors = self.model.encode(
                batch_texts,
                normalize_embeddings=True,
                convert_to_numpy=True,
                show_progress_bar=False,
            )
            batches.append(batch_vectors)
            print(f"      batch {batch_number}/{total_batches}: {len(batch_texts)} ta matn")

        vectors = np.vstack(batches).astype(np.float32)  # batch'larni bitta jadvalga birlashtirish
        self.validate(vectors, expected_count=len(texts))
        return vectors

    def validate(self, vectors: np.ndarray, expected_count: int) -> None:
        """Shakl to'g'riligini va NaN/inf yo'qligini tekshiradi. Xato bo'lsa — ValueError."""
        if vectors.shape != (expected_count, self.dimension):
            raise ValueError(
                f"Kutilgan shakl {(expected_count, self.dimension)}, olingan {vectors.shape}"
            )
        if not np.all(np.isfinite(vectors)):
            raise ValueError("Embedding ichida NaN yoki cheksiz (inf) qiymat bor")
