"""
Qdrant collection'ini ko'rib chiqish: o'lcham, point soni va bir nechta namunaviy payload.

    python scripts/inspect_collection.py
    python scripts/inspect_collection.py --limit 5

Bu similarity search EMAS — faqat nima saqlanganini tekshirish (scroll).
Qdrant server ishlayotgan bo'lsa, brauzerda ham ko'rish mumkin: http://localhost:6333/dashboard
"""

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from config.settings import get_settings  # noqa: E402
from tactiq.indexing.vector_store import QdrantStore, create_qdrant_client  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect the TACTIQ Qdrant collection")
    parser.add_argument("--limit", type=int, default=3)
    args = parser.parse_args()

    settings = get_settings()
    client = create_qdrant_client(settings.qdrant_url, settings.qdrant_api_key, settings.qdrant_local_path)
    store = QdrantStore(client, settings.qdrant_collection)

    if not client.collection_exists(settings.qdrant_collection):
        print(f"Collection '{settings.qdrant_collection}' topilmadi. Avval: python scripts/ingest_documents.py")
        return 1

    print(f"Collection:       {settings.qdrant_collection}")
    print(f"Vector dimension: {store.get_vector_dimension()}")
    print(f"Point'lar soni:   {store.count()}")

    for point in store.peek(limit=args.limit):
        payload = point.payload
        print(f"\n- id={point.id}")
        print(f"  source={payload['source']}  page={payload['page']}  chunk_index={payload['chunk_index']}")
        print(f"  document_type={payload['document_type']}  topic={payload['topic']}  language={payload['language']}")
        print(f"  token_count={payload['token_count']}  embedding_model={payload['embedding_model']}")
        print(f"  chunk_text: {payload['chunk_text'][:200]!r}...")

    client.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
