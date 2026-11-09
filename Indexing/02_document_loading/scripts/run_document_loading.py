"""
02 — Document Loading: 2.1 Load -> 2.2 Metadata -> 2.3 Text Cleaning natijasini ko'rish.

    python Indexing/02_document_loading/scripts/run_document_loading.py
    python Indexing/02_document_loading/scripts/run_document_loading.py --data-dir Indexing/01_documents/my_documents
"""

import argparse  # argparse — command line argumentlari
import json  # json.dumps — metadata dict'ini chiroyli (indent bilan) chiqarish uchun
import sys  # sys.path — import yo'llari
from pathlib import Path  # Path — fayl yo'llari

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # Indexing/ papkasi
import indexing_paths  # noqa: F401,E402

from config.settings import get_settings  # noqa: E402
from document_loading import attach_metadata, clean_document, load_directory  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="02 Document Loading")
    parser.add_argument("--data-dir", type=Path, default=None)
    args = parser.parse_args()
    data_dir = args.data_dir or get_settings().raw_data_dir

    # ---------------- 2.1 Load ----------------
    print("=== 2.1 Load: fayllardan matnni o'qish ===")
    result = load_directory(data_dir)
    for document in result.documents:
        meta = document.metadata
        page = f"page={meta['page']}" if meta["page"] else "page=None"
        print(f"  {meta['source']:<28} {page:<9} {len(document.text):>5} belgi")  # len(text) — belgilar soni
    print(f"  Yuklangan fayllar: {len(result.loaded_files)}, xato: {len(result.failed_files)}, "
          f"qo'llab-quvvatlanmagan: {len(result.skipped_files)}")
    for path, error in result.failed_files.items():
        print(f"    XATO {path}: {error}")
    if not result.documents:
        print("Hujjat topilmadi.")
        return 1

    # ---------------- 2.2 Metadata ----------------
    print("\n=== 2.2 Metadata: har bir matnga 'pasport' biriktirish ===")
    documents = [attach_metadata(document, data_dir) for document in result.documents]
    print("  Birinchi document'ning metadata'si:")
    # indent=4 — har bir kalit alohida qatorda; ensure_ascii=False — harflar o'qiladigan bo'lsin
    print(json.dumps(documents[0].metadata, indent=4, ensure_ascii=False))

    # ---------------- 2.3 Text Cleaning ----------------
    print("\n=== 2.3 Text Cleaning: oldin / keyin ===")
    cleaned = [clean_document(document) for document in documents]
    # Eng ko'p o'zgargan document'ni topamiz — farqni ko'rsatish uchun eng yaxshi misol.
    # zip(a, b) — juftlab aylanadi; max(..., key=...) — key qiymati eng katta bo'lgan elementni oladi.
    before, after = max(zip(documents, cleaned), key=lambda pair: len(pair[0].text) - len(pair[1].text))
    print(f"  Fayl: {before.metadata['source']}  ({len(before.text)} -> {len(after.text)} belgi)")
    print(f"  OLDIN: {before.text[:160]!r}")
    print(f"  KEYIN: {after.text[:160]!r}")
    print(f"  Metadata o'zgarmadimi? {before.metadata == after.metadata}")

    empty = sum(1 for document in cleaned if document.text == "")  # sum(1 for ...) — shartga mos elementlar soni
    print(f"\n  Bo'sh matnlar (o'tkazib yuboriladi): {empty}")
    print("Keyingi bosqich: 03 — Chunking.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
