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

import numpy as np  # numpy — sonlar bilan tez ishlash kutubxonasi: array (massiv/jadval), matematika va statistika.
#                     "as np" — qisqa nom (alias); numpy.zeros(...) o'rniga np.zeros(...) deb yozamiz.
#                     Embedding'lar numpy array ko'rinishida keladi: har qator — bitta matnning vector'i.
from sentence_transformers import SentenceTransformer  # sentence-transformers — matnni embedding (vector)ga aylantiruvchi
#                                                        kutubxona. SentenceTransformer — Hugging Face'dan model yuklaydi
#                                                        va .encode() metodi bilan matnni vector'ga aylantiradi.


class EmbeddingModel:
    """Sentence Transformers modelini bir marta yuklaydi va qayta-qayta ishlatadi.

    Modelni yuklash sekin (diskdan / internetdan o'qish), shuning uchun uni __init__ ichida
    bir marta yuklab, self.model'da saqlaymiz. Har bir embed() chaqiruvi tayyor modelni ishlatadi.
    Boshqa modelga o'tish uchun faqat model_name'ni o'zgartirish kifoya.

    Nima uchun dataclass emas? @dataclass faqat "self.x = x" yozadigan __init__ yaratadi.
    Bu yerda esa __init__ ISH bajaradi: modelni yuklaydi va vector o'lchamini hisoblaydi.
    model va dimension — argument emas, obyektning o'zi yaratadigan qiymatlar.
    Bunday class'lar uchun oddiy __init__ + self aniqroq va tushunarliroq.
    """

    def __init__(self, model_name: str, batch_size: int = 32):
        self.model_name = model_name  # self.model_name — keyin pipeline va Qdrant payload'ida ishlatiladi
        self.batch_size = batch_size  # bir vaqtda nechta matn model'dan o'tkaziladi
        # SentenceTransformer(...) — modelni yuklaydi (birinchi marta internetdan, keyin keshdan).
        # GPU bo'lsa uni, bo'lmasa CPU'ni o'zi tanlaydi.
        self.model = SentenceTransformer(model_name)

        # Vector o'lchamini qo'lda yozmaymiz: bitta sinov matnini embed qilib, natijadan o'qiymiz.
        test_vector = self.model.encode(["dimension check"], normalize_embeddings=True)  # natija shakli: (1, 384)
        self.dimension = int(test_vector.shape[1])  # .shape — array o'lchamlari (qatorlar, ustunlar); [1] — ustunlar soni

    # @property — metodni atribut kabi chaqirish imkonini beradi: model.max_seq_length (qavssiz).
    @property
    def max_seq_length(self) -> int:
        """Model bir vaqtda ko'ra oladigan maksimal token soni. Undan uzun matn kesib tashlanadi."""
        return int(self.model.max_seq_length)  # all-MiniLM-L6-v2 uchun 256

    def embed(self, texts: list[str]) -> np.ndarray:  # np.ndarray — numpy array turi (type hint)
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
        if len(texts) == 0:  # len() — ro'yxat uzunligi (elementlar soni)
            # np.zeros((0, 384)) — 0 qatorli, 384 ustunli bo'sh array. Bo'sh kirish -> bo'sh, lekin to'g'ri shakldagi natija.
            return np.zeros((0, self.dimension), dtype=np.float32)

        batches = []  # har bir batch natijasi (kichik array) shu ro'yxatga yig'iladi
        # "//" — butun bo'lish (qoldiqsiz). (10 + 4 - 1) // 4 = 3 — 10 ta matn uchun 3 ta batch (yuqoriga yaxlitlash).
        total_batches = (len(texts) + self.batch_size - 1) // self.batch_size
        # range(0, 100, 32) — 0, 32, 64, 96: har bir batch'ning boshlanish indeksi
        for batch_number, start in enumerate(range(0, len(texts), self.batch_size), start=1):
            batch_texts = texts[start : start + self.batch_size]  # slice: ro'yxatdan batch_size ta element
            batch_vectors = self.model.encode(  # .encode() — matnlarni vector'larga aylantiradi (embedding'ning o'zi shu yerda)
                batch_texts,
                normalize_embeddings=True,  # har bir vector uzunligini 1 ga keltirish
                convert_to_numpy=True,      # natija numpy array bo'lsin
                show_progress_bar=False,    # kutubxonaning o'z progress bar'ini o'chiramiz — o'zimiz chop etamiz
            )
            batches.append(batch_vectors)
            print(f"      batch {batch_number}/{total_batches}: {len(batch_texts)} ta matn")

        # np.vstack(...) — "vertical stack": bir nechta array'ni ustma-ust qo'yib, bitta katta jadval yasaydi.
        # .astype(np.float32) — sonlarni 32-bitli float turiga keltiramiz (Qdrant uchun yetarli, xotirani tejaydi).
        vectors = np.vstack(batches).astype(np.float32)
        self.validate(vectors, expected_count=len(texts))
        return vectors

    def validate(self, vectors: np.ndarray, expected_count: int) -> None:  # "-> None" — hech narsa qaytarmaydi
        """Embedding natijasini tekshiradi. Xato topilsa — ValueError.

        Nima uchun tekshiramiz? Noto'g'ri vector'lar Qdrant'ga jim yozilib qolsa,
        keyinchalik qidiruv sababsiz yomon ishlaydi va xatoni topish juda qiyin bo'ladi.
        """
        if vectors.shape != (expected_count, self.dimension):  # shakl to'g'rimi: (matnlar soni, 384)?
            raise ValueError(
                f"Kutilgan shakl {(expected_count, self.dimension)}, olingan {vectors.shape}"
            )
        # np.isfinite(x) — har bir son "oddiy" sonmi (NaN yoki cheksizlik emasmi) — True/False array qaytaradi.
        # np.all(...) — hammasi True bo'lsagina True.
        if not np.all(np.isfinite(vectors)):
            raise ValueError("Embedding ichida NaN yoki cheksiz (inf) qiymat bor")
