"""
Embedding Generation — 5-bosqich

Embedding nima?
    Matnning ma'nosini ifodalovchi sonlar ro'yxati (vector). Masalan:
        "high press"  ->  [0.021, -0.113, 0.087, ..., 0.045]   (384 ta son)
    Ma'nosi yaqin matnlarning vector'lari ham bir-biriga yaqin bo'ladi:
        "high press" va "aggressive pressing in the opponent's half" -> yaqin
        "high press" va "ticket prices"                               -> uzoq

Nima uchun matn vector'ga aylanadi?
    Kompyuter "ma'no"ni to'g'ridan-to'g'ri solishtira olmaydi, lekin sonlarni solishtira oladi.
    Vector'lar orasidagi masofa (cosine similarity) — ma'no yaqinligining o'lchovi.
    Bu keyinchalik semantic search'ning asosi: savol vector'iga eng yaqin chunk'larni topish.

Vector dimension (o'lcham) nima?
    Vector'dagi sonlar soni. all-MiniLM-L6-v2 uchun — 384. Har bir son ma'noning qandaydir
    "yo'nalishi"ni ifodalaydi (ular odam tushunadigan nomga ega emas). Qdrant collection'i
    aynan shu o'lcham bilan yaratilishi kerak, shuning uchun biz uni qo'lda yozmaymiz,
    model chiqargan haqiqiy vector'dan aniqlaymiz.

Nima uchun hujjatlar va savollar uchun BIR XIL model kerak?
    Har bir model o'zining "koordinatalar tizimi"ni yaratadi. A model vector'ini B model
    vector'i bilan solishtirish — ikki xil xaritadagi koordinatalarni solishtirish kabi ma'nosiz.
    Shuning uchun model nomi Qdrant payload'ida ham saqlanadi.

Input:  chunk matnlari ro'yxati
Output: numpy array, shakli (chunk_soni, dimension)

Keyingi bosqich: Qdrant Storage.
"""

import numpy as np
from sentence_transformers import SentenceTransformer


class EmbeddingModel:
    """Sentence Transformers modelini bir marta yuklaydi va qayta-qayta ishlatadi.

    Modelni yuklash sekin (diskdan / internetdan o'qish), shuning uchun uni __init__ ichida
    bir marta yuklab, self.model'da saqlaymiz. Har bir embed() chaqiruvi tayyor modelni ishlatadi.
    Boshqa modelga o'tish uchun faqat model_name'ni o'zgartirish kifoya.
    """

    def __init__(self, model_name: str, batch_size: int = 32):
        self.model_name = model_name
        self.batch_size = batch_size
        # SentenceTransformer GPU bo'lsa uni, bo'lmasa CPU'ni o'zi tanlaydi.
        self.model = SentenceTransformer(model_name)

        # Vector o'lchamini qo'lda yozmaymiz: bitta sinov matnini embed qilib, natijadan o'qiymiz.
        test_vector = self.model.encode(["dimension check"], normalize_embeddings=True)
        self.dimension = int(test_vector.shape[1])

    @property
    def max_seq_length(self) -> int:
        """Model bir vaqtda ko'ra oladigan maksimal token soni. Undan uzun matn kesib tashlanadi.

        @property — metodni atribut kabi chaqirish imkonini beradi: model.max_seq_length (qavssiz).
        """
        return int(self.model.max_seq_length)

    def embed(self, texts: list[str]) -> np.ndarray:
        """Matnlar ro'yxatini vector'larga aylantiradi (batch'lar bo'yicha).

        Batch processing nima?
            1000 ta matnni bittalab yuborish sekin; hammasini birdan yuborish esa xotirani
            to'ldirishi mumkin. Shuning uchun ularni batch_size ta (masalan 32 ta) guruhlarga
            bo'lib, har bir guruhni bitta amal bilan model'dan o'tkazamiz.

        normalize_embeddings=True nima uchun?
            Har bir vector uzunligi 1 ga keltiriladi. Shunda cosine similarity oddiy
            dot product'ga teng bo'ladi va barcha vector'lar bir xil "masshtabda" bo'ladi.
            Qdrant collection'i ham COSINE distance bilan yaratiladi — bu tanlov mos keladi.

        Input:  texts — bo'sh bo'lmagan matnlar ro'yxati.
        Output: numpy array, shakli (len(texts), self.dimension), turi float32.
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

        vectors = np.vstack(batches).astype(np.float32)  # batch'larni bitta jadvalga birlashtiramiz
        self.validate(vectors, expected_count=len(texts))
        return vectors

    def validate(self, vectors: np.ndarray, expected_count: int) -> None:
        """Embedding natijasini tekshiradi. Xato topilsa — ValueError.

        Nima uchun tekshiramiz? Noto'g'ri vector'lar Qdrant'ga jim yozilib qolsa,
        keyinchalik qidiruv sababsiz yomon ishlaydi va xatoni topish juda qiyin bo'ladi.
        """
        if vectors.shape != (expected_count, self.dimension):
            raise ValueError(
                f"Kutilgan shakl {(expected_count, self.dimension)}, olingan {vectors.shape}"
            )
        if not np.all(np.isfinite(vectors)):
            raise ValueError("Embedding ichida NaN yoki cheksiz (inf) qiymat bor")

