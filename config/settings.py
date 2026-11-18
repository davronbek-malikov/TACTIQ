"""
Settings — barcha sozlamalar bitta joyda.

Qiymatlar .env faylidan (environment variable) o'qiladi, bo'lmasa — default ishlatiladi.
.env git'ga tushmaydi (parol va API key'lar uchun). Namuna: .env.example
"""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent  # config/settings.py -> loyiha ildizi
load_dotenv(PROJECT_ROOT / ".env")                     # .env bo'lmasa — hech narsa qilmaydi


def is_offline() -> bool:
    """TACTIQ_OFFLINE=1 — internetsiz rejim: faqat local LLM (qwen), Hugging Face'ga so'rov yo'q."""
    return os.getenv("TACTIQ_OFFLINE", "").strip() == "1"


if is_offline():  # transformers import qilinishidan OLDIN bo'lishi shart — model faqat keshdan olinadi
    os.environ.setdefault("HF_HUB_OFFLINE", "1")
    os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")


def _read_int(name: str, default: int) -> int:
    """Environment variable'ni int sifatida o'qiydi."""
    value = os.getenv(name)
    if value is None or value.strip() == "":
        return default
    return int(value)


def _read_optional(name: str) -> Optional[str]:
    """Bo'sh qiymatni None deb oladi."""
    value = os.getenv(name)
    if value is None or value.strip() == "":
        return None
    return value.strip()


@dataclass(frozen=True)  # frozen — sozlamalar ish davomida tasodifan o'zgarmasin
class Settings:
    # --- Fayllar ---
    raw_data_dir: Path = PROJECT_ROOT / "Indexing" / "01_documents" / "sample_docs"   # 01 — hujjatlar
    processed_data_dir: Path = PROJECT_ROOT / "Indexing" / "03_chunking" / "output"   # chunks.jsonl

    # --- Chunking (token'da) ---
    chunk_size: int = 500
    chunk_overlap: int = 50

    # --- Embedding ---
    embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_batch_size: int = 32

    # --- Qdrant ---
    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: Optional[str] = None
    qdrant_collection: str = "tactiq_documents"
    qdrant_local_path: Optional[str] = None   # berilsa — Docker'siz, diskdagi papkada ishlaydi


def _read_path(name: str, default: Path) -> Path:
    """Yo'lni o'qiydi. Nisbiy yo'l loyiha ildiziga nisbatan olinadi."""
    value = os.getenv(name)
    if value is None or value.strip() == "":
        return default
    path = Path(value.strip())
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    return path


def get_settings() -> Settings:
    """.env / environment variable'lardan Settings yaratadi."""
    defaults = Settings()
    qdrant_url = os.getenv("QDRANT_URL", defaults.qdrant_url)
    local_path = _read_optional("QDRANT_LOCAL_PATH")
    if is_offline() and not local_path and not qdrant_url.startswith(("http://localhost", "http://127.0.0.1")):
        raise ValueError("Offline rejim: Qdrant Cloud ishlamaydi. QDRANT_LOCAL_PATH yoki Docker (localhost) ishlating.")
    return Settings(
        raw_data_dir=_read_path("TACTIQ_RAW_DATA_DIR", defaults.raw_data_dir),
        processed_data_dir=_read_path("TACTIQ_PROCESSED_DATA_DIR", defaults.processed_data_dir),
        chunk_size=_read_int("TACTIQ_CHUNK_SIZE", defaults.chunk_size),
        chunk_overlap=_read_int("TACTIQ_CHUNK_OVERLAP", defaults.chunk_overlap),
        embedding_model_name=os.getenv("TACTIQ_EMBEDDING_MODEL", defaults.embedding_model_name),
        embedding_batch_size=_read_int("TACTIQ_EMBEDDING_BATCH_SIZE", defaults.embedding_batch_size),
        qdrant_url=qdrant_url,
        qdrant_api_key=_read_optional("QDRANT_API_KEY"),
        qdrant_collection=os.getenv("QDRANT_COLLECTION", defaults.qdrant_collection),
        qdrant_local_path=local_path,
    )
