"""
05 — Vector Database: vector + matn + metadata'ni Qdrant'ga saqlash.

Bu oxirgi bosqich, shuning uchun 02 -> 03 -> 04 -> 05 hammasi ishlaydi (butun pipeline).
Keyin Qdrant'da nima saqlanganini ko'rsatadi.

    docker compose up -d qdrant          # avval Qdrant'ni ishga tushiring
    python Indexing/05_vector_database/scripts/step1_run_vector_database.py

Ikki marta ishga tushirib ko'ring: point'lar soni o'zgarmasligi kerak (barqaror ID + upsert).
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # Indexing/ papkasi
import indexing_paths  # noqa: F401,E402

from config.settings import get_settings  # noqa: E402
from indexing_pipeline import run_indexing_pipeline  # noqa: E402  — 02..05 hammasi
from vector_database import QdrantStore, create_qdrant_client  # noqa: E402  — 05


def main() -> int:
    settings = get_settings()
    parser = argparse.ArgumentParser(description="05 Vector Database (Qdrant)")
    parser.add_argument("--data-dir", type=Path, default=None)
    args = parser.parse_args()

    summary = run_indexing_pipeline(settings, data_dir=args.data_dir)
    if summary.vectors_stored == 0:
        return 1

    # Qdrant'da saqlangan bitta point'ni ko'rsatamiz: id + payload (vector — 384 ta son, ko'rsatmaymiz)
    client = create_qdrant_client(settings.qdrant_url, settings.qdrant_api_key, settings.qdrant_local_path)
    store = QdrantStore(client, settings.qdrant_collection)
    point = store.peek(limit=1)[0]
    print("\n=== Qdrant'dagi bitta point ===")
    print(f"  id:      {point.id}")
    print(f"  vector:  {store.get_vector_dimension()} ta son (Distance: COSINE)")
    print("  payload:")
    for key, value in point.payload.items():
        if key == "chunk_text":
            value = value[:80] + "..."  # uzun matnni qisqartirib ko'rsatamiz
        print(f"    {key:<16} {value!r}")
    client.close()

    print("\nBrauzerda ko'rish: http://localhost:6333/dashboard")
    print("Batafsil: python Indexing/05_vector_database/scripts/step2_inspect_collection.py")
    return 1 if summary.failed_files else 0


if __name__ == "__main__":
    sys.exit(main())
