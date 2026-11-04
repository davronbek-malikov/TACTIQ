"""3-bosqich: Embedding — matn -> vector (Hugging Face, sentence-transformers).

Muhim qoida: hujjatlarni va savollarni BIR XIL model bilan embed qilish kerak.
Shu sababli bu class Retrieval pipeline'da ham qayta ishlatiladi (embed_query).
"""

import numpy as np
import torch
from sentence_transformers import SentenceTransformer

from config import EMBEDDING_BATCH_SIZE, EMBEDDING_MODEL


class Embedder:
    def __init__(self, model_name: str = EMBEDDING_MODEL, device: str | None = None):
        self.model_name = model_name
        device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        # GPU'da fp16 (Colab T4), CPU'da float32 (CPU'da bf16/fp16 sekinroq ishlaydi)
        dtype = torch.float16 if device == "cuda" else torch.float32
        self.model = SentenceTransformer(model_name, device=device, model_kwargs={"dtype": dtype})

    @property
    def dimension(self) -> int:
        return self.model.get_embedding_dimension()

    @property
    def tokenizer(self):
        """Chunking shu tokenizer bilan o'lchanadi (chunk_size token'da)."""
        return self.model.tokenizer

    def embed_documents(self, texts: list[str], batch_size: int = EMBEDDING_BATCH_SIZE) -> np.ndarray:
        # normalize_embeddings=True -> vector uzunligi 1, cosine similarity = dot product
        return self.model.encode_document(
            texts,
            batch_size=batch_size,
            normalize_embeddings=True,
            show_progress_bar=True,
        )

    def embed_query(self, text: str) -> np.ndarray:
        # Qwen3-Embedding savol uchun maxsus "query" prompt'ini qo'shadi (encode_query buni o'zi qiladi)
        return self.model.encode_query(text, normalize_embeddings=True)
