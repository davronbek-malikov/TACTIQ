"""
Settings — loyiha sozlamalari

Bu modul barcha sozlamalarni (fayl yo'llari, chunk o'lchami, embedding model nomi,
Qdrant manzili) bitta joyda saqlaydi. Sozlamalar environment variable'lardan o'qiladi,
agar ular berilmagan bo'lsa — default qiymat ishlatiladi.

Environment variable nima?
    Operatsion tizim darajasidagi "kalit = qiymat" juftligi. Masalan:
        QDRANT_URL=http://localhost:6333
    Ularni kodga yozmaymiz (hard-code qilmaymiz), chunki:
      * parol va API key'lar GitHub'ga tushib qolmasligi kerak;
      * bir xil kod turli muhitda (laptop, server, cloud) turli sozlama bilan ishlashi kerak.
    `.env` fayli — shu o'zgaruvchilarni yozib qo'yadigan oddiy matn fayl.
    U `.gitignore`da, ya'ni hech qachon commit qilinmaydi. Namuna: `.env.example`.
"""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

# Path — fayl yo'llari bilan ishlash uchun class (pathlib moduli).
# Oddiy string o'rniga Path ishlatsak, "/" operatori bilan yo'llarni qo'shish mumkin
# va kod Windows hamda Linux'da bir xil ishlaydi.
# __file__ — shu faylning yo'li. .parent ikki marta: config/settings.py -> config/ -> loyiha ildizi.
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# .env faylini o'qib, ichidagi qiymatlarni environment variable'larga qo'shadi.
# Fayl bo'lmasa — xato bermaydi, shunchaki hech narsa qilmaydi.
load_dotenv(PROJECT_ROOT / ".env")


def _read_int(name: str, default: int) -> int:
    """Environment variable'ni butun son (int) sifatida o'qiydi.

    Environment variable'lar doim string bo'ladi, shuning uchun int() ga aylantiramiz.
    """
    value = os.getenv(name)
    if value is None or value.strip() == "":
        return default
    return int(value)


def _read_optional(name: str) -> Optional[str]:
    """Bo'sh string'ni None deb hisoblaydi (".env"da `QDRANT_API_KEY=` bo'sh qolishi mumkin)."""
    value = os.getenv(name)
    if value is None or value.strip() == "":
        return None
    return value.strip()


# @dataclass — class yozishni soddalashtiradigan decorator.
# Biz faqat atributlarni (nom + type hint + default qiymat) yozamiz,
# Python esa __init__(), __repr__() va __eq__() metodlarini avtomatik yaratadi.
# Ya'ni `Settings(chunk_size=300)` deb obyekt yaratish mumkin, constructor'ni qo'lda yozmaymiz.
#
# frozen=True — obyekt yaratilgandan keyin uning qiymatlarini o'zgartirib bo'lmaydi.
# Sozlamalar pipeline davomida tasodifan o'zgarib qolmasligi uchun shunday qilamiz.
@dataclass(frozen=True)
class Settings:
    # Type hint (masalan `: Path`, `: int`) — qiymat qanday turda bo'lishi kerakligini bildiradi.
    # Python buni majburlamaydi, lekin kodni o'qish va IDE yordami uchun juda foydali.

    # --- Fayllar ---
    raw_data_dir: Path = PROJECT_ROOT / "data" / "raw"
    processed_data_dir: Path = PROJECT_ROOT / "data" / "processed"

    # --- Chunking ---
    chunk_size: int = 500     # bitta chunk'dagi maksimal token soni
    chunk_overlap: int = 50   # qo'shni chunk'lar orasida takrorlanadigan token soni

    # --- Embeddings ---
    embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_batch_size: int = 32

    # --- Qdrant ---
    # Optional[str] — qiymat yo string, yo None bo'lishi mumkin degani.
    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: Optional[str] = None
    qdrant_collection: str = "tactiq_documents"
    # Agar berilsa, Qdrant server o'rniga diskdagi papkada ishlaydigan "local mode" ishlatiladi
    # (Docker o'rnatilmagan kompyuterlar uchun qulay).
    qdrant_local_path: Optional[str] = None


def get_settings() -> Settings:
    """Environment variable'lardan Settings obyektini yaratadi.

    Output: Settings — butun pipeline shu obyekt orqali sozlanadi.
    """
    defaults = Settings()
    return Settings(
        raw_data_dir=Path(os.getenv("TACTIQ_RAW_DATA_DIR", str(defaults.raw_data_dir))),
        processed_data_dir=Path(os.getenv("TACTIQ_PROCESSED_DATA_DIR", str(defaults.processed_data_dir))),
        chunk_size=_read_int("TACTIQ_CHUNK_SIZE", defaults.chunk_size),
        chunk_overlap=_read_int("TACTIQ_CHUNK_OVERLAP", defaults.chunk_overlap),
        embedding_model_name=os.getenv("TACTIQ_EMBEDDING_MODEL", defaults.embedding_model_name),
        embedding_batch_size=_read_int("TACTIQ_EMBEDDING_BATCH_SIZE", defaults.embedding_batch_size),
        qdrant_url=os.getenv("QDRANT_URL", defaults.qdrant_url),
        qdrant_api_key=_read_optional("QDRANT_API_KEY"),
        qdrant_collection=os.getenv("QDRANT_COLLECTION", defaults.qdrant_collection),
        qdrant_local_path=_read_optional("QDRANT_LOCAL_PATH"),
    )
