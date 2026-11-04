"""
Chunking — 4-bosqich

Uzun hujjatni kichik, bir-birini qisman qoplaydigan bo'laklarga (chunk) bo'lamiz.

Nima uchun bo'lamiz?
  1. Embedding model bir vaqtda cheklangan miqdordagi token'ni "ko'ra oladi"
     (all-MiniLM-L6-v2 uchun max_seq_length = 256 token; undan uzun matn kesib tashlanadi).
  2. Kichik chunk = aniqroq ma'no. 20 sahifali hujjatning bitta vector'i hamma narsani
     "o'rtacha" qilib yuboradi; kichik chunk esa bitta aniq g'oyani ifodalaydi.
  3. Kelajakda LLM'ga butun hujjatni emas, faqat kerakli chunk'larni beramiz.

Fixed-size chunking (token bo'yicha), chunk_size = 500, overlap = 50:

    token'lar: [0 ................ 499]
                                [450 ................ 949]
                                                   [900 ......... oxiri]
               |<-- chunk_size -->|
                                |<->| overlap: 50 token ikkala chunk'da ham bor

    step = chunk_size - overlap = 450  (har yangi chunk 450 token oldinga siljiydi)

Overlap nima uchun kerak? Muhim gap ikki chunk chegarasida bo'linib qolsa,
overlap tufayli u kamida bittasida to'liq saqlanadi.

Token nima? Model matnni so'zlarga emas, token'larga bo'lib o'qiydi:
    "counterpressing" -> ["counter", "##pressing"]   (2 token)
Shuning uchun chunk o'lchamini embedding model'ning O'Z tokenizer'i bilan o'lchaymiz.

Input:  tozalangan, metadata'ga ega Document'lar
Output: Chunk'lar ro'yxati (chunk_id, document_id, text, metadata)

Keyingi bosqich: Embedding Generation.
"""

import uuid  # uuid — barqaror chunk_id yasash uchun (uuid5)
from dataclasses import dataclass, field  # Chunk — ma'lumot saqlovchi class, shuning uchun dataclass
from typing import Iterator  # Iterator[X] — "X'larni bittadan beradigan obyekt" (generator) uchun type hint

from transformers import AutoTokenizer  # transformers — Hugging Face kutubxonasi.
#                                         AutoTokenizer — model nomi bo'yicha unga mos tokenizer'ni avtomatik yuklaydi
#                                         (matnni token'larga bo'luvchi qism).

from indexing.step1_document_loading import Document  # 1-bosqichdagi Document
from indexing.step2_metadata import TACTIQ_NAMESPACE  # document_id bilan bir xil namespace — ID'lar bir tizimda


@dataclass
class Chunk:
    """Bitta chunk — Qdrant'ga yoziladigan eng kichik birlik.

    chunk_id:    barqaror UUID (Qdrant'da point ID sifatida ishlatiladi).
    document_id: chunk qaysi hujjatdan olingani.
    text:        chunk matni (asl matndan aynan kesib olingan, o'zgartirilmagan).
    metadata:    hujjat metadata'si + chunk_index va token_count.
    """

    chunk_id: str
    document_id: str
    text: str
    metadata: dict = field(default_factory=dict)  # har bir Chunk uchun alohida yangi dict


def make_token_windows(token_count: int, chunk_size: int, overlap: int) -> Iterator[tuple[int, int]]:
    """Token'lar ketma-ketligini (start, end) oynalarga (window) bo'ladi.

    Bu funksiya tokenizer'ga bog'liq emas — faqat sonlar bilan ishlaydi.
    Shuning uchun overlap mantiqini alohida, oson test qilish mumkin.

    Misol: token_count=10, chunk_size=4, overlap=1  ->  (0,4) (3,7) (6,10)

    Input:  token_count — matndagi token'lar soni; chunk_size; overlap.
    Output: (start, end) juftlari; end — oxirgi token'dan keyingi indeks (Python slice kabi).
            tuple[int, int] — ikkita butun sondan iborat juftlik, masalan (0, 500).
    """
    # Noto'g'ri sozlamalarni darhol rad etamiz — aks holda sikl hech qachon tugamasligi mumkin.
    if chunk_size <= 0:
        raise ValueError(f"chunk_size musbat bo'lishi kerak, berildi: {chunk_size}")
    if overlap < 0 or overlap >= chunk_size:
        raise ValueError(f"overlap 0 <= overlap < chunk_size bo'lishi kerak, berildi: {overlap}")

    step = chunk_size - overlap  # har bir yangi oyna shuncha token oldinga siljiydi
    start = 0
    while start < token_count:  # while — shart True bo'lgunicha takrorlanadigan sikl
        end = min(start + chunk_size, token_count)  # min() — kichigini oladi: oxirgi oyna matn chegarasidan chiqmasin
        # yield — bu funksiyani generator'ga aylantiradi. U barcha natijani ro'yxatga yig'ib
        # bir vaqtda qaytarmaydi, balki har bir (start, end) juftini so'ralganda bittadan beradi.
        # list(make_token_windows(...)) deb yozsak — hammasini ro'yxat qilib olamiz.
        yield (start, end)
        if end == token_count:  # matn oxiriga yetdik — to'xtaymiz
            break  # break — sikldan darhol chiqadi
        start += step  # start = start + step


def make_chunk_id(document_id: str, page, chunk_index: int) -> str:
    """Barqaror chunk_id: bir xil hujjat + sahifa + tartib raqam -> har doim bir xil UUID."""
    return str(uuid.uuid5(TACTIQ_NAMESPACE, f"chunk:{document_id}:{page}:{chunk_index}"))


class TokenTextSplitter:
    """Matnni token soni bo'yicha chunk'larga bo'luvchi class.

    Nima uchun dataclass emas? __init__ faqat qiymat saqlamaydi — u tokenizer va sozlamalarni
    TEKSHIRADI. Bunday "ish bajaradigan" class'lar uchun oddiy class yozamiz.
    Tokenizer'ni bir marta yuklab (sekin amal), keyin ko'p hujjat uchun qayta ishlatamiz.
    """

    def __init__(self, tokenizer, chunk_size: int = 500, chunk_overlap: int = 50):
        # __init__ — obyekt yaratilganda bir marta ishlaydi: TokenTextSplitter(tokenizer, 500, 50)
        # self.<nom> = ... — qiymatni shu obyektga "yopishtirib" qo'yadi, boshqa metodlar
        # (masalan split_text) uni self.chunk_size orqali o'qiy oladi.

        # getattr(obyekt, "nom", default) — atributni nomi bo'yicha oladi; bo'lmasa default qaytaradi.
        # "Fast" tokenizer (Rust'da yozilgan) offset'larni qaytara oladi — bizga aynan shu kerak.
        if not getattr(tokenizer, "is_fast", False):
            raise ValueError("Fast tokenizer kerak (return_offsets_mapping uchun).")
        # Sozlamalarni darhol tekshiramiz (noto'g'ri bo'lsa — shu yerda xato beradi).
        list(make_token_windows(0, chunk_size, chunk_overlap))

        self.tokenizer = tokenizer
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    # @classmethod — obyekt emas, class'ning o'zi orqali chaqiriladigan metod:
    #     TokenTextSplitter.from_model_name("...")
    # cls — class'ning o'zi (self obyektni bildirganidek). cls(...) — yangi obyekt yaratadi.
    # Bu "muqobil constructor": tokenizer o'rniga model nomini berib obyekt yaratish usuli.
    @classmethod
    def from_model_name(cls, model_name: str, chunk_size: int = 500, chunk_overlap: int = 50):
        """Hugging Face'dan model nomi bo'yicha tokenizer'ni yuklab, splitter yaratadi.

        Embedding model bilan BIR XIL tokenizer bo'lishi kerak — aks holda "500 token"
        embedding model uchun boshqa son bo'lib chiqadi.
        """
        tokenizer = AutoTokenizer.from_pretrained(model_name)  # birinchi marta internetdan yuklaydi, keyin keshdan (cache) oladi
        return cls(tokenizer, chunk_size, chunk_overlap)

    def split_text(self, text: str) -> list[tuple[str, int]]:
        """Bitta matnni chunk'larga bo'ladi.

        Qanday ishlaydi:
          1. Tokenizer matnni token'larga bo'ladi va har bir token'ning asl matndagi
             joylashuvini (offset: boshlanish va tugash belgisi) qaytaradi.
          2. make_token_windows() token oynalarini hisoblaydi.
          3. Har bir oynaning birinchi token boshi va oxirgi token oxiri bo'yicha
             ASL matndan kesib olamiz.
        Nima uchun decode() emas? all-MiniLM tokenizer'i "uncased": decode() matnni kichik
        harfga o'tkazadi va bo'sh joylarni buzadi. Offset orqali kesish asl matnni saqlaydi.

        Output: [(chunk_text, token_count), ...]. Bo'sh chunk'lar qaytarilmaydi.
        """
        # self.tokenizer(...) — tokenizer obyektini funksiya kabi chaqiramiz; u dict'ga o'xshash natija qaytaradi.
        encoding = self.tokenizer(
            text,
            add_special_tokens=False,       # [CLS]/[SEP] kabi maxsus token'larni sanamaymiz
            return_offsets_mapping=True,    # har token uchun (boshlanish, tugash) belgi indeksi
            verbose=False,                  # "matn juda uzun" ogohlantirishini o'chiramiz — biz o'zimiz bo'lamiz
        )
        offsets = encoding["offset_mapping"]  # masalan [(0, 4), (5, 10), ...] — har bir token matnning qayerida

        pieces = []
        for start, end in make_token_windows(len(offsets), self.chunk_size, self.chunk_overlap):
            char_start = offsets[start][0]   # oynadagi birinchi token'ning boshlanish belgisi
            char_end = offsets[end - 1][1]   # oynadagi oxirgi token'ning tugash belgisi
            chunk_text = text[char_start:char_end].strip()  # text[a:b] — slice: a'dan b'gacha bo'lgan qism
            if chunk_text:  # bo'sh chunk yaratmaymiz
                pieces.append((chunk_text, end - start))  # (matn, token_soni) juftligi
        return pieces

    def split_document(self, document: Document) -> list[Chunk]:
        """Bitta Document'ni Chunk'larga aylantiradi, metadata'ni har bir chunk'ga ko'chiradi."""
        document_id = document.metadata["document_id"]
        page = document.metadata.get("page")

        chunks = []
        # enumerate(...) — (tartib_raqam, element) juftlarini beradi; element o'zi ham juftlik bo'lgani uchun
        # (chunk_text, token_count) deb ochib (unpack) olamiz.
        for chunk_index, (chunk_text, token_count) in enumerate(self.split_text(document.text)):
            # {**a, "x": 1} — a dict'ning nusxasi + yangi kalitlar. Asl metadata o'zgarmaydi.
            # ** — "dict ichidagi barcha kalit:qiymatlarni shu yerga yoy" degani.
            chunk_metadata = {**document.metadata, "chunk_index": chunk_index, "token_count": token_count}
            chunks.append(
                Chunk(
                    chunk_id=make_chunk_id(document_id, page, chunk_index),
                    document_id=document_id,
                    text=chunk_text,
                    metadata=chunk_metadata,
                )
            )
        return chunks

    def split_documents(self, documents: list[Document]) -> list[Chunk]:
        """Bir nechta Document'ni bo'ladi va barcha chunk'larni bitta ro'yxatga yig'adi."""
        all_chunks = []
        for document in documents:
            all_chunks.extend(self.split_document(document))  # .extend() — ro'yxatdagi barcha chunk'larni qo'shadi
        return all_chunks
