"""
03 — Chunking: uzun matnni token bo'yicha kichik, bir-birini qoplaydigan bo'laklarga bo'ladi.

chunk_size = 500, overlap = 50:
    [0 ........ 500]
              [450 ........ 950]
                         [900 ...... oxiri]
    har yangi chunk 450 token (500 - 50) oldinga siljiydi; 50 token ikkala chunk'da ham bor.

Token — model o'qiydigan bo'lak: "counterpressing" -> ["counter", "##pressing"].
Shuning uchun embedding model'ning o'z tokenizer'i bilan o'lchaymiz.

Keyingi bosqich: 04 — Embedding Model
"""

import uuid
from dataclasses import dataclass, field
from typing import Iterator

from transformers import AutoTokenizer  # Hugging Face: model nomi bo'yicha tokenizer yuklaydi

from document_loading import TACTIQ_NAMESPACE, Document


@dataclass
class Chunk:
    """Qdrant'ga yoziladigan eng kichik birlik."""

    chunk_id: str        # barqaror UUID (Qdrant point ID)
    document_id: str     # qaysi hujjatdan
    text: str            # asl matndan kesilgan bo'lak
    metadata: dict = field(default_factory=dict)  # hujjat metadata'si + chunk_index, token_count


def make_token_windows(token_count: int, chunk_size: int, overlap: int) -> Iterator[tuple[int, int]]:
    """(start, end) oynalarini bittadan beradi. Misol: 10 token, 4/1 -> (0,4) (3,7) (6,10)."""
    if chunk_size <= 0:
        raise ValueError(f"chunk_size musbat bo'lishi kerak, berildi: {chunk_size}")
    if overlap < 0 or overlap >= chunk_size:
        raise ValueError(f"overlap 0 <= overlap < chunk_size bo'lishi kerak, berildi: {overlap}")

    step = chunk_size - overlap
    start = 0
    while start < token_count:
        end = min(start + chunk_size, token_count)
        yield (start, end)  # yield — natijani bittadan beradi (generator)
        if end == token_count:
            break
        start += step


def make_chunk_id(document_id: str, page, chunk_index: int) -> str:
    """Bir xil hujjat + sahifa + tartib raqam -> har doim bir xil ID."""
    return str(uuid.uuid5(TACTIQ_NAMESPACE, f"chunk:{document_id}:{page}:{chunk_index}"))


class TokenTextSplitter:
    """Matnni token soni bo'yicha chunk'larga bo'ladi. Tokenizer bir marta yuklanadi."""

    def __init__(self, tokenizer, chunk_size: int = 500, chunk_overlap: int = 50):
        if not getattr(tokenizer, "is_fast", False):  # offset'lar uchun "fast" tokenizer kerak
            raise ValueError("Fast tokenizer kerak (return_offsets_mapping uchun).")
        list(make_token_windows(0, chunk_size, chunk_overlap))  # sozlamalarni darhol tekshirish

        self.tokenizer = tokenizer
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    @classmethod
    def from_model_name(cls, model_name: str, chunk_size: int = 500, chunk_overlap: int = 50):
        """Model nomidan splitter yaratadi: TokenTextSplitter.from_model_name("...")."""
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        return cls(tokenizer, chunk_size, chunk_overlap)

    def split_text(self, text: str) -> list[tuple[str, int]]:
        """Matnni [(chunk_text, token_count), ...] ga bo'ladi.

        decode() o'rniga offset bilan ASL matndan kesamiz — decode() matnni kichik harfga o'tkazadi.
        """
        encoding = self.tokenizer(
            text,
            add_special_tokens=False,      # [CLS]/[SEP] sanalmaydi
            return_offsets_mapping=True,   # har token matnning qayerida: (boshlanish, tugash)
            verbose=False,
        )
        offsets = encoding["offset_mapping"]

        pieces = []
        for start, end in make_token_windows(len(offsets), self.chunk_size, self.chunk_overlap):
            char_start = offsets[start][0]   # oynadagi birinchi token boshi
            char_end = offsets[end - 1][1]   # oynadagi oxirgi token oxiri
            chunk_text = text[char_start:char_end].strip()
            if chunk_text:
                pieces.append((chunk_text, end - start))
        return pieces

    def split_document(self, document: Document) -> list[Chunk]:
        """Bitta Document -> Chunk'lar (metadata har bir chunk'ga ko'chiriladi)."""
        document_id = document.metadata["document_id"]
        page = document.metadata.get("page")

        chunks = []
        for chunk_index, (chunk_text, token_count) in enumerate(self.split_text(document.text)):
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
        """Bir nechta Document -> barcha chunk'lar bitta ro'yxatda."""
        all_chunks = []
        for document in documents:
            all_chunks.extend(self.split_document(document))
        return all_chunks
