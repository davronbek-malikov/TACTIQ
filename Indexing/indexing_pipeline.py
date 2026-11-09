"""
Indexing Pipeline — 5 bosqichni ketma-ket ishga tushiradi:

    01 Documents -> 02 Document Loading -> 03 Chunking -> 04 Embedding Model -> 05 Vector Database

Natija: to'ldirilgan Qdrant collection (keyingi Retrieval & Generation pipeline shundan qidiradi).

    python Indexing/indexing_pipeline.py
    python Indexing/indexing_pipeline.py --data-dir Indexing/01_documents/my_documents
"""

import argparse
import json
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Optional

import indexing_paths  # noqa: F401  — config/ va har bir bosqichning src/ papkasini import qilish uchun

from config.settings import Settings, get_settings
from document_loading import attach_metadata, clean_document, load_directory  # 02
from chunking import Chunk, TokenTextSplitter                                  # 03
from embedding_model import EmbeddingModel                                     # 04
from vector_database import QdrantStore, create_qdrant_client                  # 05


@dataclass
class IndexingSummary:
    """Pipeline natijasi — barcha sonlar haqiqiy ishdan hisoblanadi."""

    data_dir: str
    discovered_files: int = 0
    loaded_files: int = 0
    failed_files: dict = field(default_factory=dict)
    unsupported_files: list = field(default_factory=list)
    text_sections: int = 0            # PDF sahifalari + boshqa fayllar
    empty_sections_skipped: int = 0   # tozalashdan keyin bo'sh qolganlar
    chunks_created: int = 0
    vectors_stored: int = 0
    collection_total_points: int = 0
    embedding_model: str = ""
    vector_dimension: int = 0
    collection_name: str = ""
    collection_created: bool = False
    warnings: list = field(default_factory=list)

    def print_report(self) -> None:
        print("\n========== TACTIQ Indexing Summary ==========")
        print(f"01 Data papkasi:               {self.data_dir}")
        print(f"   Topilgan fayllar:           {self.discovered_files}")
        print(f"02 Muvaffaqiyatli yuklangan:   {self.loaded_files}")
        print(f"   Xato bergan fayllar:        {len(self.failed_files)}")
        for path, error in self.failed_files.items():
            print(f"      - {path}: {error}")
        print(f"   Qo'llab-quvvatlanmagan:     {len(self.unsupported_files)}")
        print(f"   Matn bo'limlari (sahifa/fayl): {self.text_sections}")
        print(f"   Bo'sh, o'tkazib yuborilgan: {self.empty_sections_skipped}")
        print(f"03 Yaratilgan chunk'lar:       {self.chunks_created}")
        print(f"04 Embedding model:            {self.embedding_model} (dimension={self.vector_dimension})")
        print(f"05 Qdrant collection:          {self.collection_name} "
              f"({'yangi yaratildi' if self.collection_created else 'avvaldan mavjud'})")
        print(f"   Qdrant'ga yozilgan vector'lar: {self.vectors_stored}")
        print(f"   Collection'dagi jami point'lar: {self.collection_total_points}")
        for warning in self.warnings:
            print(f"OGOHLANTIRISH: {warning}")
        print("=============================================")


def save_chunks_for_inspection(chunks: list[Chunk], output_dir: Path) -> Path:
    """Chunk'larni chunks.jsonl ga yozadi (har qatorda bitta chunk) — ko'z bilan tekshirish uchun."""
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "chunks.jsonl"
    with output_path.open("w", encoding="utf-8") as file:
        for chunk in chunks:
            file.write(json.dumps(asdict(chunk), ensure_ascii=False) + "\n")
    return output_path


def run_indexing_pipeline(
    settings: Settings,
    data_dir: Optional[Path] = None,
    qdrant_store: Optional[QdrantStore] = None,
    embedding_model: Optional[EmbeddingModel] = None,
    save_chunks: bool = True,
) -> IndexingSummary:
    """Butun pipeline'ni ishga tushiradi. qdrant_store va embedding_model testlar uchun tashqaridan berilishi mumkin."""
    data_dir = Path(data_dir or settings.raw_data_dir)
    summary = IndexingSummary(data_dir=str(data_dir))

    # --- 01 + 02.1 Load ---
    print(f"\n[01] Documents: {data_dir}")
    print("[02] Document Loading")
    print("     2.1 Load")
    load_result = load_directory(data_dir)
    summary.loaded_files = len(load_result.loaded_files)
    summary.failed_files = load_result.failed_files
    summary.unsupported_files = load_result.skipped_files
    summary.discovered_files = summary.loaded_files + len(summary.failed_files) + len(summary.unsupported_files)
    summary.text_sections = len(load_result.documents)
    print(f"         {summary.discovered_files} fayl topildi, {summary.loaded_files} tasi yuklandi, "
          f"{len(summary.failed_files)} tasi xato berdi")

    # --- 02.2 Metadata ---
    print("     2.2 Metadata")
    documents_with_metadata = [attach_metadata(document, data_dir) for document in load_result.documents]
    print(f"         {len(documents_with_metadata)} ta matn bo'limiga document_id va metadata biriktirildi")

    # --- 02.3 Cleaning (bo'sh matnlar tashlab yuboriladi) ---
    print("     2.3 Text Cleaning")
    cleaned_documents = []
    for document in documents_with_metadata:
        cleaned = clean_document(document)
        if cleaned.text == "":
            summary.empty_sections_skipped += 1
            continue
        cleaned_documents.append(cleaned)
    print(f"         {len(cleaned_documents)} ta matn bo'limi tozalandi, "
          f"{summary.empty_sections_skipped} tasi bo'sh bo'lgani uchun o'tkazib yuborildi")

    if not cleaned_documents:
        summary.warnings.append("Indexing uchun matn topilmadi. 01_documents papkasiga PDF/DOCX/TXT/MD fayl qo'ying.")
        summary.print_report()
        return summary

    # --- 03 Chunking ---
    print(f"[03] Chunking: chunk_size={settings.chunk_size}, overlap={settings.chunk_overlap} token")
    splitter = TokenTextSplitter.from_model_name(
        settings.embedding_model_name, settings.chunk_size, settings.chunk_overlap
    )
    chunks = splitter.split_documents(cleaned_documents)
    summary.chunks_created = len(chunks)
    print(f"     {len(chunks)} ta chunk yaratildi")
    if save_chunks:
        saved_path = save_chunks_for_inspection(chunks, settings.processed_data_dir)
        print(f"     chunk'lar tekshirish uchun saqlandi: {saved_path}")

    # --- 04 Embedding Model ---
    print(f"[04] Embedding Model: {settings.embedding_model_name}")
    if embedding_model is None:
        embedding_model = EmbeddingModel(settings.embedding_model_name, settings.embedding_batch_size)
    summary.embedding_model = embedding_model.model_name
    summary.vector_dimension = embedding_model.dimension

    if settings.chunk_size > embedding_model.max_seq_length:  # chunk oxiri vector'ga kirmaydi — ogohlantiramiz
        summary.warnings.append(
            f"chunk_size ({settings.chunk_size}) model max_seq_length ({embedding_model.max_seq_length}) "
            f"dan katta: har bir chunk'ning {embedding_model.max_seq_length}-tokendan keyingi qismi "
            f"embedding'ga kirmaydi (truncation). TACTIQ_CHUNK_SIZE ni kamaytirishni ko'rib chiqing."
        )

    vectors = embedding_model.embed([chunk.text for chunk in chunks])
    print(f"     vectors.shape = {vectors.shape}  (chunk'lar soni, vector dimension)")

    # --- 05 Vector Database ---
    print(f"[05] Vector Database: Qdrant collection '{settings.qdrant_collection}'")
    created_here = qdrant_store is None
    if created_here:
        client = create_qdrant_client(settings.qdrant_url, settings.qdrant_api_key, settings.qdrant_local_path)
        qdrant_store = QdrantStore(client, settings.qdrant_collection)
    summary.collection_name = qdrant_store.collection_name
    summary.collection_created = qdrant_store.ensure_collection(embedding_model.dimension)
    summary.vectors_stored = qdrant_store.upsert_chunks(chunks, vectors, embedding_model.model_name)
    summary.collection_total_points = qdrant_store.count()
    if created_here:
        qdrant_store.client.close()  # o'zimiz ochgan ulanishni yopamiz

    summary.print_report()
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="TACTIQ indexing pipeline: 01 -> 05")
    parser.add_argument("--data-dir", type=Path, default=None,
                        help="Hujjatlar papkasi (default: Indexing/01_documents/sample_docs)")
    parser.add_argument("--no-save-chunks", action="store_true", help="chunks.jsonl yozilmasin")
    args = parser.parse_args()

    summary = run_indexing_pipeline(get_settings(), data_dir=args.data_dir, save_chunks=not args.no_save_chunks)
    return 1 if summary.failed_files else 0  # exit code: 0 — hammasi yaxshi, 1 — xato bergan fayl bor


if __name__ == "__main__":
    sys.exit(main())
