"""
indexing_paths — config/, Indexing/ va har bir bosqichning src/ papkasini sys.path'ga qo'shadi.
Shunda `import config`, `import document_loading`, `import chunking` ... hamma joyda ishlaydi.

Skriptlarda:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # Indexing/ papkasi
    import indexing_paths
"""

import sys
from pathlib import Path

INDEXING_DIR = Path(__file__).resolve().parent    # .../Indexing
PROJECT_ROOT = INDEXING_DIR.parent                # loyiha ildizi (config/ shu yerda)
SRC_DIRS = sorted(INDEXING_DIR.glob("*/src"))     # 02, 03, 04, 05 bosqichlarning src/ papkalari

for folder in [PROJECT_ROOT, INDEXING_DIR, *SRC_DIRS]:
    if str(folder) not in sys.path:
        sys.path.insert(0, str(folder))

import config.settings  # noqa: E402,F401  — .env + offline rejim, transformers'dan OLDIN yuklansin
