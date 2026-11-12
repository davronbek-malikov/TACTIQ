"""
rag_paths — import yo'llarini sozlaydi: config/, Indexing paketlari va har bir 0X_ bosqich papkasi.

Har bir faylning boshida:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # Retrieval_Generation/
    import rag_paths
"""

import sys
from pathlib import Path

RAG_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = RAG_DIR.parent

sys.path.insert(0, str(PROJECT_ROOT / "Indexing"))
import indexing_paths  # noqa: E402,F401  — config/ + Indexing paketlari (EmbeddingModel, Qdrant)

for folder in [RAG_DIR, *sorted(RAG_DIR.glob("0*_*"))]:  # 01_user_question ... 07_answer_sources
    if str(folder) not in sys.path:
        sys.path.insert(0, str(folder))
