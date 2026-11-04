"""2-bosqich: Chunking — uzun Document'ni kichik, bir-birini qoplaydigan bo'laklarga bo'lish.

Fixed-size chunking (token bo'yicha):

    tokenlar:  [0 ........ 499]
                         [450 ........ 949]
                                     [900 ........ 1399]
               |<- chunk_size ->|
                         |<-->| overlap = 50

Nima uchun token? Embedding model matnni token'larda ko'radi va uning max_seq_length'i
ham token'da. Shuning uchun chunk'ni embedding model'ning o'z tokenizer'i bilan o'lchaymiz.
"""

import uuid
from dataclasses import dataclass, field

from indexing_pipeline.data_loading import Document

# Bir xil fayl + sahifa + tartib raqam -> doim bir xil ID.
# Natija: pipeline'ni qayta ishga tushirsak, Qdrant'da dublikat emas, yangilanish bo'ladi.
CHUNK_ID_NAMESPACE = uuid.UUID("6f1c2a52-6b1e-4c1a-9a57-0b8f2d0c5e11")


@dataclass
class Chunk:
    id: str
    text: str
    metadata: dict = field(default_factory=dict)


def split_tokens(token_ids: list[int], chunk_size: int, overlap: int) -> list[list[int]]:
    if not 0 <= overlap < chunk_size:
        raise ValueError(f"overlap ({overlap}) 0 dan katta va chunk_size ({chunk_size}) dan kichik bo'lishi kerak")

    step = chunk_size - overlap
    windows = []
    for start in range(0, len(token_ids), step):
        windows.append(token_ids[start : start + chunk_size])
        if start + chunk_size >= len(token_ids):  # oxirgi bo'lak — to'xtaymiz
            break
    return windows


def chunk_documents(
    documents: list[Document],
    tokenizer,
    chunk_size: int,
    overlap: int,
) -> list[Chunk]:
    chunks = []
    for doc in documents:
        token_ids = tokenizer.encode(doc.text, add_special_tokens=False)
        for index, window in enumerate(split_tokens(token_ids, chunk_size, overlap)):
            text = tokenizer.decode(window).strip()
            if not text:
                continue
            key = f"{doc.metadata['source']}|{doc.metadata.get('page')}|{index}"
            chunks.append(
                Chunk(
                    id=str(uuid.uuid5(CHUNK_ID_NAMESPACE, key)),
                    text=text,
                    metadata={**doc.metadata, "chunk_index": index, "n_tokens": len(window)},
                )
            )
    return chunks
