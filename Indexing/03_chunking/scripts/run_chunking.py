"""
03 — Chunking: matnni token bo'yicha kichik qismlarga bo'lish va overlap'ni ko'rish.

    python Indexing/03_chunking/scripts/run_chunking.py
    python Indexing/03_chunking/scripts/run_chunking.py --chunk-size 120 --overlap 20

Kichik chunk_size bilan ishga tushirsangiz, overlap'ni ko'z bilan ko'rish osonroq.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # Indexing/ papkasi
import indexing_paths  # noqa: F401,E402

from config.settings import get_settings  # noqa: E402
from document_loading import attach_metadata, clean_document, load_directory  # noqa: E402  — 02-bosqich
from chunking import TokenTextSplitter, make_token_windows  # noqa: E402  — 03-bosqich


def main() -> int:
    settings = get_settings()
    parser = argparse.ArgumentParser(description="03 Chunking")
    parser.add_argument("--data-dir", type=Path, default=None)
    parser.add_argument("--chunk-size", type=int, default=settings.chunk_size)
    parser.add_argument("--overlap", type=int, default=settings.chunk_overlap)
    args = parser.parse_args()
    data_dir = args.data_dir or settings.raw_data_dir

    # 02 — Document Loading (oldingi bosqich): o'qish -> metadata -> tozalash
    documents = [clean_document(attach_metadata(d, data_dir)) for d in load_directory(data_dir).documents]
    documents = [d for d in documents if d.text]  # bo'sh matnlarni tashlaymiz

    # 1) Oyna (window) matematikasi — tokenizer'siz, faqat sonlar
    print(f"=== Window matematikasi: 1200 token, chunk_size={args.chunk_size}, overlap={args.overlap} ===")
    print(" ", list(make_token_windows(1200, args.chunk_size, args.overlap)))

    # 2) Tokenizer — embedding model'ning o'zi bilan bir xil
    splitter = TokenTextSplitter.from_model_name(settings.embedding_model_name, args.chunk_size, args.overlap)
    print(f"\n=== Token nima? ({settings.embedding_model_name} tokenizer'i) ===")
    print(" ", splitter.tokenizer.tokenize("Counterpressing after losing the ball"))  # .tokenize — matn -> token'lar

    # 3) Har bir hujjatni chunk'larga bo'lamiz
    chunks = splitter.split_documents(documents)
    print(f"\n=== {len(documents)} ta matn bo'limi -> {len(chunks)} ta chunk ===")
    for chunk in chunks:
        meta = chunk.metadata
        print(f"  {meta['source']:<28} page={str(meta['page']):<5} chunk_index={meta['chunk_index']}  "
              f"tokens={meta['token_count']:<4} id={chunk.chunk_id[:8]}...")

    # 4) Overlap'ni ko'rsatamiz: bir hujjatning ketma-ket ikki chunk'i
    for document in documents:
        document_chunks = [c for c in chunks if c.document_id == document.metadata["document_id"]
                           and c.metadata["page"] == document.metadata["page"]]
        if len(document_chunks) >= 2:
            print(f"\n=== Overlap: {document.metadata['source']} ===")
            print(f"  1-chunk OXIRI : ...{document_chunks[0].text[-120:]!r}")
            print(f"  2-chunk BOSHI : {document_chunks[1].text[:120]!r}...")
            break
    else:  # for ... else — sikl break'siz tugasa ishlaydi (ya'ni 2 ta chunk'li hujjat topilmadi)
        print("\n(Hech bir hujjat 2+ chunk'ga bo'linmadi. Overlap'ni ko'rish uchun: --chunk-size 120 --overlap 20)")

    print("\nKeyingi bosqich: 04 — Embedding Model.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
