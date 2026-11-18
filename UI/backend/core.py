"""
core — backend uchun umumiy resurslar: sozlamalar, embedding model va bitta Qdrant ulanishi.

Model va ulanish bir marta yaratiladi va barcha so'rovlar uchun qayta ishlatiladi.
Qdrant local rejimida (QDRANT_LOCAL_PATH) faqat bitta ulanish bo'lishi mumkin — shuning uchun hammasi shu yerda.
"""

import contextlib  # nullcontext — server rejimida "bo'sh" qulf
import sys
import threading   # Lock — bir vaqtda bitta Qdrant/model amali
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BACKEND_DIR.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "Retrieval_Generation"))
import rag_paths  # noqa: E402,F401  — config/, Indexing va Retrieval_Generation paketlari

from config.settings import Settings, get_settings  # noqa: E402
from embedding_model import EmbeddingModel  # noqa: E402
from vector_database import QdrantStore, create_qdrant_client  # noqa: E402

APP_VERSION = "0.1.0"
RUNTIME_DIR = BACKEND_DIR / "runtime"  # indexing tarixi shu yerda (git'ga tushmaydi)

settings: Settings = get_settings()

# Local rejimda Qdrant faqat bitta ulanish va ketma-ket amallarni qo'llaydi -> qulf.
# Server rejimida (Docker) client parallel so'rovlarni o'zi boshqaradi -> qulf kerak emas.
qdrant_lock = threading.RLock() if settings.qdrant_local_path else contextlib.nullcontext()

_model = None
_client = None
_model_lock = threading.Lock()
_client_lock = threading.Lock()


def get_embedding_model() -> EmbeddingModel:
    """Embedding model birinchi kerak bo'lganda yuklanadi (Indexing'dagi aynan o'sha model)."""
    global _model
    with _model_lock:
        if _model is None:
            _model = EmbeddingModel(settings.embedding_model_name, settings.embedding_batch_size)
        return _model


def get_qdrant_client():
    global _client
    with _client_lock:
        if _client is None:
            _client = create_qdrant_client(settings.qdrant_url, settings.qdrant_api_key, settings.qdrant_local_path)
        return _client


def get_store(collection: str = None) -> QdrantStore:
    return QdrantStore(get_qdrant_client(), collection or settings.qdrant_collection)


def qdrant_mode() -> dict:
    """Qdrant qayerda ishlayapti (kalit va parollarsiz)."""
    if settings.qdrant_local_path:
        return {"mode": "local", "location": settings.qdrant_local_path}
    return {"mode": "server", "location": settings.qdrant_url}


def check_qdrant() -> dict:
    """Haqiqiy ulanishni tekshiradi. Ulanmasa — xato matni bilan connected=False."""
    try:
        with qdrant_lock:
            names = [c.name for c in get_qdrant_client().get_collections().collections]
        return {**qdrant_mode(), "connected": True, "collections": names, "error": None}
    except Exception as error:
        return {**qdrant_mode(), "connected": False, "collections": [], "error": f"{type(error).__name__}: {error}"}


def close() -> None:
    global _client
    with _client_lock:
        if _client is not None:
            _client.close()
            _client = None
