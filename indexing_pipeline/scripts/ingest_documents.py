"""
TACTIQ Indexing pipeline'ni command line'dan ishga tushirish.

Misollar:
    python indexing_pipeline/scripts/ingest_documents.py                              # data/raw/ papkasi
    python indexing_pipeline/scripts/ingest_documents.py --data-dir data/sample_docs  # namunaviy hujjatlar
"""

import argparse  # argparse — command line argumentlarini (--data-dir kabi) o'qish uchun standart kutubxona
import sys  # sys — Python interpretatori bilan ishlash: import yo'llari (sys.path), dasturdan chiqish (sys.exit)
from pathlib import Path  # Path — fayl yo'llari

# Loyiha ildizini (config/ uchun) va indexing_pipeline/src/ ni Python import yo'liga (sys.path) qo'shamiz.
# Shunda `import config` va `import indexing` loyihani o'rnatmasdan (pip install) ishlaydi.
# __file__ — shu skript faylining yo'li; .resolve() — to'liq (absolute) yo'lga aylantiradi; .parent — bitta yuqori papka.
PIPELINE_DIR = Path(__file__).resolve().parent.parent   # indexing_pipeline/
PROJECT_ROOT = PIPELINE_DIR.parent                      # TACTIQ/ (config/ shu yerda)
sys.path.insert(0, str(PROJECT_ROOT))                   # sys.path — Python modullarni qidiradigan papkalar ro'yxati
sys.path.insert(0, str(PIPELINE_DIR / "src"))           # insert(0, ...) — ro'yxat boshiga qo'shish (birinchi bo'lib qidiriladi)

from config.settings import get_settings  # noqa: E402  (sys.path'dan keyin import qilinishi shart)
from indexing.pipeline import run_indexing_pipeline  # noqa: E402  ("noqa" — kod tekshiruvchi vositaga "bu ataylab" degani)


def main() -> int:
    """Argumentlarni o'qiydi, pipeline'ni ishga tushiradi va exit code qaytaradi."""
    parser = argparse.ArgumentParser(description="TACTIQ document indexing pipeline")
    # add_argument — qabul qilinadigan argumentni e'lon qilamiz; type=Path — matnni avtomatik Path'ga aylantiradi
    parser.add_argument("--data-dir", type=Path, default=None, help="Hujjatlar papkasi (default: data/raw)")
    # action="store_true" — flag: yozilsa True, yozilmasa False (qiymat kerak emas)
    parser.add_argument("--no-save-chunks", action="store_true", help="data/processed/chunks.jsonl yozilmasin")
    args = parser.parse_args()  # command line'dagi haqiqiy qiymatlarni o'qiydi: args.data_dir, args.no_save_chunks

    settings = get_settings()  # .env va environment variable'lardan sozlamalar
    summary = run_indexing_pipeline(settings, data_dir=args.data_dir, save_chunks=not args.no_save_chunks)

    # Exit code: 0 — hammasi yaxshi, 1 — kamida bitta fayl xato berdi (CI / skriptlar uchun foydali).
    return 1 if summary.failed_files else 0


# __name__ == "__main__" — fayl to'g'ridan-to'g'ri ishga tushirilganda True bo'ladi
# (boshqa fayldan import qilinganda esa main() avtomatik ishlamaydi).
if __name__ == "__main__":
    sys.exit(main())  # sys.exit(kod) — dasturni shu exit code bilan tugatadi
