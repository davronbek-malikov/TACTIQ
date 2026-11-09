"""
Qdrant collection'ini ko'rib chiqish: o'lcham, point soni va bir nechta namunaviy payload.

    python Indexing/05_vector_database/scripts/inspect_collection.py
    python Indexing/05_vector_database/scripts/inspect_collection.py --limit 5

Bu similarity search EMAS — faqat nima saqlanganini tekshirish (scroll).
Qdrant server ishlayotgan bo'lsa, brauzerda ham ko'rish mumkin: http://localhost:6333/dashboard
"""

import argparse  # argparse — command line argumentlarini (--limit) o'qish
import sys  # sys — import yo'llari (sys.path) va dasturdan chiqish (sys.exit)
from pathlib import Path  # Path — fayl yo'llari

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # Indexing/ papkasi
import indexing_paths  # noqa: F401,E402  — config/ va barcha src/ papkalarni import qilish mumkin qiladi

from config.settings import get_settings  # noqa: E402
from vector_database import QdrantStore, create_qdrant_client  # noqa: E402  — faqat 05-bosqich kerak


def main() -> int:
    """Collection haqidagi ma'lumotni va bir nechta point'ni ekranga chiqaradi."""
    parser = argparse.ArgumentParser(description="Inspect the TACTIQ Qdrant collection")
    parser.add_argument("--limit", type=int, default=3)  # nechta point ko'rsatish
    args = parser.parse_args()

    settings = get_settings()
    client = create_qdrant_client(settings.qdrant_url, settings.qdrant_api_key, settings.qdrant_local_path)
    store = QdrantStore(client, settings.qdrant_collection)

    if not client.collection_exists(settings.qdrant_collection):
        print(f"Collection '{settings.qdrant_collection}' topilmadi. Avval: python Indexing/05_vector_database/scripts/run_vector_database.py")
        return 1

    print(f"Collection:       {settings.qdrant_collection}")
    print(f"Vector dimension: {store.get_vector_dimension()}")
    print(f"Point'lar soni:   {store.count()}")

    for point in store.peek(limit=args.limit):
        payload = point.payload  # payload — dict: chunk_text, source, page ...
        print(f"\n- id={point.id}")
        print(f"  source={payload['source']}  page={payload['page']}  chunk_index={payload['chunk_index']}")
        print(f"  document_type={payload['document_type']}  topic={payload['topic']}  language={payload['language']}")
        print(f"  token_count={payload['token_count']}  embedding_model={payload['embedding_model']}")
        # [:200] — faqat birinchi 200 belgi; !r — qiymatni repr() ko'rinishida (qo'shtirnoq va \n bilan) chiqaradi
        print(f"  chunk_text: {payload['chunk_text'][:200]!r}...")

    client.close()  # ulanishni yopamiz
    return 0


if __name__ == "__main__":
    sys.exit(main())
