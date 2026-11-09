"""
indexing_paths — Indexing papkasidagi barcha kodlarni import qilish mumkin qiladi.

Muammo: har bir bosqichning kodi o'z papkasida turibdi, masalan:
    Indexing/02_document_loading/src/document_loading/
    Indexing/03_chunking/src/chunking/
Python esa paketlarni faqat sys.path ro'yxatidagi papkalardan qidiradi.

Yechim: shu faylni import qilsak, u quyidagilarni sys.path'ga qo'shadi:
    * loyiha ildizi        -> `import config` ishlaydi (umumiy sozlamalar)
    * Indexing/ papkasi    -> `import indexing_pipeline` ishlaydi
    * har bir */src papka  -> `import document_loading`, `import chunking`, ... ishlaydi

Skriptlarda ishlatilishi:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # Indexing/ papkasi
    import indexing_paths  # noqa: F401
"""

import sys  # sys.path — Python modullarni qidiradigan papkalar ro'yxati
from pathlib import Path  # Path — fayl yo'llari

INDEXING_DIR = Path(__file__).resolve().parent  # .../TACTIQ/Indexing
PROJECT_ROOT = INDEXING_DIR.parent              # .../TACTIQ  (config/ shu yerda)

# glob("*/src") — Indexing ichidagi har bir bosqich papkasidagi "src" papkalarni topadi.
# sorted(...) — 02, 03, 04, 05 tartibida.
SRC_DIRS = sorted(INDEXING_DIR.glob("*/src"))

for folder in [PROJECT_ROOT, INDEXING_DIR, *SRC_DIRS]:  # *SRC_DIRS — ro'yxat elementlarini shu ro'yxatga "yoyadi"
    if str(folder) not in sys.path:  # bir papkani ikki marta qo'shmaymiz
        sys.path.insert(0, str(folder))
