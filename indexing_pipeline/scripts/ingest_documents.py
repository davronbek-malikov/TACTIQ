"""
TACTIQ Indexing pipeline'ni command line'dan ishga tushirish.

Misollar:
    python indexing_pipeline/scripts/ingest_documents.py                              # data/raw/ papkasi
    python indexing_pipeline/scripts/ingest_documents.py --data-dir data/sample_docs  # namunaviy hujjatlar
"""

import argparse
import sys
from pathlib import Path

# Loyiha ildizini (config/ uchun) va indexing_pipeline/src/ ni Python import yo'liga (sys.path) qo'shamiz.
# Shunda `import config` va `import indexing` loyihani o'rnatmasdan (pip install) ishlaydi.
PIPELINE_DIR = Path(__file__).resolve().parent.parent   # indexing_pipeline/
PROJECT_ROOT = PIPELINE_DIR.parent                      # TACTIQ/ (config/ shu yerda)
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PIPELINE_DIR / "src"))

from config.settings import get_settings  # noqa: E402  (sys.path'dan keyin import qilinishi shart)
from indexing.pipeline import run_indexing_pipeline  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="TACTIQ document indexing pipeline")
    parser.add_argument("--data-dir", type=Path, default=None, help="Hujjatlar papkasi (default: data/raw)")
    parser.add_argument("--no-save-chunks", action="store_true", help="data/processed/chunks.jsonl yozilmasin")
    args = parser.parse_args()

    settings = get_settings()
    summary = run_indexing_pipeline(settings, data_dir=args.data_dir, save_chunks=not args.no_save_chunks)

    # Exit code: 0 — hammasi yaxshi, 1 — kamida bitta fayl xato berdi (CI / skriptlar uchun foydali).
    return 1 if summary.failed_files else 0


if __name__ == "__main__":
    sys.exit(main())
