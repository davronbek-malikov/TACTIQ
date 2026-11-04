"""Indexing pipeline'ni boshidan oxirigacha ishga tushirish.

    cd rag_project
    python -m indexing_pipeline.run_indexing --recreate
    python -m indexing_pipeline.run_indexing --test-query "OASIS Pro narxi qancha?"
"""

import argparse
import time
from pathlib import Path

from config import CHUNK_OVERLAP, CHUNK_SIZE, COLLECTION_NAME, DATA_DIR, EMBEDDING_MODEL
from indexing_pipeline.chunking import chunk_documents
from indexing_pipeline.data_loading import load_directory
from indexing_pipeline.embedding import Embedder
from indexing_pipeline.storing import create_collection, get_client, upsert_chunks


def run(data_dir: Path, chunk_size: int, overlap: int, recreate: bool, test_query: str | None) -> None:
    t0 = time.perf_counter()

    print(f"\n[1/4] Document loading: {data_dir}")
    documents = load_directory(data_dir)
    print(f"      -> {len(documents)} document")
    if not documents:
        print("      Hech qanday fayl topilmadi. data/raw/ ichiga PDF / TXT / DOCX qo'ying.")
        return

    print(f"\n[2/4] Chunking: chunk_size={chunk_size}, overlap={overlap} (token)")
    embedder = Embedder(EMBEDDING_MODEL)  # tokenizer kerak bo'lgani uchun model shu yerda yuklanadi
    chunks = chunk_documents(documents, embedder.tokenizer, chunk_size, overlap)
    print(f"      -> {len(chunks)} chunk")
    example = chunks[0]
    print(f"      misol: {example.metadata}")
    print(f"             {example.text[:120]!r}...")

    print(f"\n[3/4] Embedding: {EMBEDDING_MODEL}")
    vectors = embedder.embed_documents([c.text for c in chunks])
    print(f"      -> vectors.shape = {vectors.shape}")

    print(f"\n[4/4] Storing -> Qdrant collection '{COLLECTION_NAME}'")
    client = get_client()
    create_collection(client, COLLECTION_NAME, embedder.dimension, recreate=recreate)
    upsert_chunks(client, COLLECTION_NAME, chunks, vectors)
    total = client.count(COLLECTION_NAME).count
    print(f"      -> collection'da jami {total} point")

    print(f"\nTayyor: {time.perf_counter() - t0:.1f} s")

    if test_query:
        # Kichik tekshiruv (smoke test). To'liq retrieval keyingi pipeline'da.
        print(f"\n[test] Savol: {test_query}")
        hits = client.query_points(
            COLLECTION_NAME, query=embedder.embed_query(test_query).tolist(), limit=3
        ).points
        for hit in hits:
            p = hit.payload
            print(f"  score={hit.score:.3f}  {p['source']} (page={p['page']}, dept={p['department']})")
            print(f"     {p['text'][:150]!r}")

    client.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="RAG indexing pipeline")
    parser.add_argument("--data-dir", type=Path, default=DATA_DIR)
    parser.add_argument("--chunk-size", type=int, default=CHUNK_SIZE)
    parser.add_argument("--overlap", type=int, default=CHUNK_OVERLAP)
    parser.add_argument("--recreate", action="store_true", help="collection'ni o'chirib, noldan yaratish")
    parser.add_argument("--test-query", type=str, default=None)
    args = parser.parse_args()
    run(args.data_dir, args.chunk_size, args.overlap, args.recreate, args.test_query)


if __name__ == "__main__":
    main()
