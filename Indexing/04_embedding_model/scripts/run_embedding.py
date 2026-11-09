"""
04 — Embedding Model: har bir chunk uchun vector yaratish va ma'no yaqinligini ko'rish.

    python Indexing/04_embedding_model/scripts/run_embedding.py
"""

import argparse  # argparse — command line argumentlari
import sys  # sys.path — import yo'llari
from pathlib import Path  # Path — fayl yo'llari

import numpy as np  # numpy — vector'lar bilan hisob-kitob (uzunlik, dot product)

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # Indexing/ papkasi
import indexing_paths  # noqa: F401,E402

from config.settings import get_settings  # noqa: E402
from document_loading import attach_metadata, clean_document, load_directory  # noqa: E402  — 02
from chunking import TokenTextSplitter  # noqa: E402  — 03
from embedding_model import EmbeddingModel  # noqa: E402  — 04


def main() -> int:
    settings = get_settings()
    parser = argparse.ArgumentParser(description="04 Embedding Model")
    parser.add_argument("--data-dir", type=Path, default=None)
    args = parser.parse_args()
    data_dir = args.data_dir or settings.raw_data_dir

    # 02 + 03 — oldingi bosqichlar
    documents = [clean_document(attach_metadata(d, data_dir)) for d in load_directory(data_dir).documents]
    documents = [d for d in documents if d.text]
    splitter = TokenTextSplitter.from_model_name(settings.embedding_model_name, settings.chunk_size, settings.chunk_overlap)
    chunks = splitter.split_documents(documents)

    # 04 — Embedding
    print(f"=== Model: {settings.embedding_model_name} ===")
    model = EmbeddingModel(settings.embedding_model_name, settings.embedding_batch_size)
    print(f"  Vector dimension: {model.dimension}  (har bir vector'dagi sonlar soni)")
    print(f"  max_seq_length:   {model.max_seq_length} token (model bir vaqtda ko'ra oladigan maksimal uzunlik)")
    if settings.chunk_size > model.max_seq_length:
        print(f"  DIQQAT: chunk_size={settings.chunk_size} > {model.max_seq_length} — chunk oxiri embedding'ga kirmaydi.")

    print(f"\n=== {len(chunks)} ta chunk -> vector'lar ===")
    vectors = model.embed([chunk.text for chunk in chunks])
    print(f"  vectors.shape = {vectors.shape}  (chunk'lar soni, dimension)")
    print(f"  1-chunk ({chunks[0].metadata['source']}) vector'ining 8 ta soni:")
    print(" ", np.round(vectors[0][:8], 4))  # np.round(x, 4) — 4 xonagacha yaxlitlash
    # np.linalg.norm — vector uzunligi. normalize_embeddings=True bo'lgani uchun ~1.0 bo'lishi kerak
    print(f"  vector uzunligi (norm): {np.linalg.norm(vectors[0]):.4f}")

    print("\n=== Ma'no yaqinligi (cosine similarity = dot product, chunki vector'lar normalize qilingan) ===")
    phrases = ["high press", "aggressive pressing in the opponent's half", "stadium ticket prices"]
    a, b, c = model.embed(phrases)  # uchta vector'ni uchta o'zgaruvchiga ochib olamiz
    print(f"  '{phrases[0]}' <-> '{phrases[1]}' : {float(a @ b):.3f}")  # "@" — dot product (matritsa ko'paytmasi)
    print(f"  '{phrases[0]}' <-> '{phrases[2]}' : {float(a @ c):.3f}")
    print("  Ma'nosi yaqin matnlar — kattaroq son.")

    print("\nKeyingi bosqich: 05 — Vector Database.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
