"""Loyiha sozlamalari (config) — barcha "magic number"lar bitta joyda.

Indexing pipeline ham, Retrieval & Generation pipeline ham shu faylni o'qiydi,
shuning uchun ikkala pipeline bir xil embedding model va bir xil collection bilan ishlaydi.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent
load_dotenv(PROJECT_ROOT / ".env")  # .env bo'lmasa — jim o'tib ketadi

# --- 1. Data loading ---------------------------------------------------------
# data/raw/<department>/<fayl>  ->  papka nomi metadata'dagi "department" bo'ladi
DATA_DIR = PROJECT_ROOT / "data" / "raw"
DEFAULT_LANGUAGE = "uz"

# --- 2. Chunking --------------------------------------------------------------
# O'lcham token'da (so'z yoki belgida emas). 4-darsdagi misol: 500 / 50.
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

# --- 3. Embedding -------------------------------------------------------------
# Qwen3-Embedding-0.6B: multilingual, 1024-o'lchamli vector, CPU'da ham ishlaydi.
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "Qwen/Qwen3-Embedding-0.6B")
EMBEDDING_BATCH_SIZE = 8

# --- 4. Storing (Qdrant) ------------------------------------------------------
# QDRANT_URL berilmasa -> local mode (Docker'siz, diskdagi papka).
# QDRANT_URL berilsa   -> Docker (http://localhost:6333) yoki Qdrant Cloud.
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
QDRANT_LOCAL_PATH = PROJECT_ROOT / "qdrant_db"
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "oasis_docs")
