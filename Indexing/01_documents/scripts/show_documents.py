"""
01 — Documents: pipeline'ga qanday fayllar kirishini ko'rish.

Bu skript hech narsani o'zgartirmaydi — faqat papkadagi fayllarni ko'rsatadi:
format, hajm, pipeline uni o'qiy oladimi va yonida .meta.json (sidecar) bormi.

    python Indexing/01_documents/scripts/show_documents.py
    python Indexing/01_documents/scripts/show_documents.py --data-dir Indexing/01_documents/my_documents
"""

import argparse  # argparse — command line argumentlarini (--data-dir) o'qish
import json  # json — .meta.json sidecar fayllarni o'qish
import sys  # sys.path — import yo'llari
from pathlib import Path  # Path — fayl va papka yo'llari

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # Indexing/ papkasi; parents[2] — 2 papka yuqori
import indexing_paths  # noqa: F401,E402  — config/ va barcha src/ papkalarni import qilish mumkin qiladi

from config.settings import get_settings  # noqa: E402

# 02 — Document Loading aynan shu formatlarni o'qiy oladi
SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md"}


def main() -> int:
    parser = argparse.ArgumentParser(description="01 Documents: papkadagi fayllarni ko'rsatish")
    parser.add_argument("--data-dir", type=Path, default=None)
    args = parser.parse_args()

    data_dir = args.data_dir or get_settings().raw_data_dir
    print(f"Papka: {data_dir}\n")

    # rglob("*") — ichki papkalar bilan birga barcha elementlar; is_file() — faqat fayllar
    files = [p for p in sorted(data_dir.rglob("*")) if p.is_file() and not p.name.startswith(".")]
    documents = [p for p in files if not p.name.endswith(".meta.json")]  # sidecar'lar alohida sanaladi

    # f"{x:<28}" — x'ni 28 belgilik joyga chapdan tekislab yozadi (jadval ko'rinishi uchun)
    header = ["Fayl", "Format", "Hajm", "O'qiladimi?"]
    print(f"{header[0]:<28} {header[1]:<7} {header[2]:>9}  {header[3]:<12} Sidecar (topic)")
    print("-" * 80)  # "-" * 80 — 80 ta chiziqcha
    for path in documents:
        size_kb = path.stat().st_size / 1024  # .stat().st_size — fayl hajmi baytlarda; /1024 -> KB
        supported = "ha" if path.suffix.lower() in SUPPORTED_EXTENSIONS else "YO'Q"
        sidecar = path.with_name(path.name + ".meta.json")
        if sidecar.exists():
            topic = json.loads(sidecar.read_text(encoding="utf-8")).get("topic")
            sidecar_info = f"bor ({topic})"
        else:
            sidecar_info = "yo'q -> metadata None bo'ladi"
        print(f"{path.name:<28} {path.suffix:<7} {size_kb:>7.1f}KB  {supported:<12} {sidecar_info}")

    print(f"\nJami: {len(documents)} ta hujjat. Keyingi bosqich: 02 — Document Loading.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
