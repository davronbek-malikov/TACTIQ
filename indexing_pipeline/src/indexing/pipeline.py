"""
Indexing Pipeline — barcha bosqichlarni ketma-ket bog'laydi

    1. Discover + Load   (step1_document_loading)  fayllarni topish va matnni o'qish
    2. Metadata          (step2_metadata)          document_id, source, page, topic ...
    3. Clean             (step3_text_cleaning)     matnni ehtiyotkorlik bilan tozalash
    4. Chunk             (step4_chunking)          500 token / 50 overlap bo'laklar
    5. Embed             (step5_embeddings)        har bir chunk -> vector
    6. Store             (step6_vector_store)      vector + payload -> Qdrant

Bu pipeline foydalanuvchi savol berishidan OLDIN ishlaydi. Uning natijasi —
to'ldirilgan Qdrant collection'i. Keyingi (hali amalga oshirilmagan) Retrieval moduli
aynan shu collection'dan qidiradi.

Har bir bosqich o'z modulida yashaydi. Bu fayl faqat ularni tartib bilan chaqiradi
va haqiqiy natijalarni (IndexingSummary) yig'adi.
"""

import json  # json — chunk'larni JSON matn ko'rinishida faylga yozish uchun
from dataclasses import asdict, dataclass, field  # asdict — dataclass obyektini oddiy dict'ga aylantiradi
from pathlib import Path  # Path — fayl yo'llari
from typing import Optional  # Optional[X] — "X yoki None"

from config.settings import Settings  # loyiha sozlamalari (chunk_size, model nomi, Qdrant manzili ...)
# Har bir bosqichdan faqat kerakli funksiya/class'ni import qilamiz — tartib ham pipeline tartibi bilan bir xil:
from indexing.step1_document_loading import load_directory                 # 1. fayllarni yuklash
from indexing.step2_metadata import attach_metadata                        # 2. metadata biriktirish
from indexing.step3_text_cleaning import clean_document                    # 3. matnni tozalash
from indexing.step4_chunking import Chunk, TokenTextSplitter               # 4. chunk'larga bo'lish
from indexing.step5_embeddings import EmbeddingModel                       # 5. vector'ga aylantirish
from indexing.step6_vector_store import QdrantStore, create_qdrant_client  # 6. Qdrant'ga yozish


@dataclass
class IndexingSummary:
    """Pipeline natijasi. Barcha sonlar haqiqiy ishdan hisoblanadi — hech biri qo'lda yozilmagan."""

    data_dir: str                     # default qiymatsiz atribut — obyekt yaratishda berilishi SHART
    discovered_files: int = 0         # "= 0" — default qiymat; berilmasa 0 bo'ladi
    loaded_files: int = 0
    failed_files: dict = field(default_factory=dict)
    unsupported_files: list = field(default_factory=list)
    text_sections: int = 0            # PDF sahifalari + boshqa fayllar
    empty_sections_skipped: int = 0   # tozalashdan keyin bo'sh qolgan sahifa/fayllar
    chunks_created: int = 0
    vectors_stored: int = 0
    collection_total_points: int = 0
    embedding_model: str = ""
    vector_dimension: int = 0
    collection_name: str = ""
    collection_created: bool = False
    warnings: list = field(default_factory=list)

    def print_report(self) -> None:
        """Yakuniy hisobotni ekranga chiqaradi (dataclass'ga ham oddiy metod qo'shish mumkin)."""
        print("\n========== TACTIQ Indexing Summary ==========")
        print(f"Data papkasi:                {self.data_dir}")
        print(f"Topilgan fayllar:            {self.discovered_files}")
        print(f"Muvaffaqiyatli yuklangan:    {self.loaded_files}")
        print(f"Xato bergan fayllar:         {len(self.failed_files)}")
        for path, error in self.failed_files.items():  # .items() — dict'dagi (kalit, qiymat) juftlari
            print(f"    - {path}: {error}")
        print(f"Qo'llab-quvvatlanmagan:      {len(self.unsupported_files)}")
        print(f"Matn bo'limlari (sahifa/fayl): {self.text_sections}")
        print(f"Bo'sh, o'tkazib yuborilgan:  {self.empty_sections_skipped}")
        print(f"Yaratilgan chunk'lar:        {self.chunks_created}")
        print(f"Qdrant'ga yozilgan vector'lar: {self.vectors_stored}")
        print(f"Embedding model:             {self.embedding_model} (dimension={self.vector_dimension})")
        # "A if shart else B" — bir qatorli shart (conditional expression)
        print(f"Qdrant collection:           {self.collection_name} "
              f"({'yangi yaratildi' if self.collection_created else 'avvaldan mavjud'})")
        print(f"Collection'dagi jami point'lar: {self.collection_total_points}")
        for warning in self.warnings:
            print(f"OGOHLANTIRISH: {warning}")
        print("=============================================")


def save_chunks_for_inspection(chunks: list[Chunk], output_dir: Path) -> Path:
    """Chunk'larni JSONL faylga yozadi (har qatorda bitta chunk) — ko'z bilan tekshirish uchun.

    JSONL — "JSON Lines": har bir qator alohida JSON obyekt. Katta fayllarni qatorma-qator o'qish oson.
    """
    # parents=True — oraliq papkalar ham yaratilsin; exist_ok=True — papka bor bo'lsa xato bermasin
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "chunks.jsonl"
    with output_path.open("w", encoding="utf-8") as file:  # "w" — yozish rejimi (fayl bor bo'lsa, qaytadan yoziladi)
        for chunk in chunks:
            # json.dumps(...) — dict'ni JSON matnga aylantiradi.
            # ensure_ascii=False — "Gündoğan" kabi harflar "\u00fc" ko'rinishidagi kodlarga aylanmasin, o'qiladigan qolsin.
            file.write(json.dumps(asdict(chunk), ensure_ascii=False) + "\n")
    return output_path


def run_indexing_pipeline(
    settings: Settings,
    data_dir: Optional[Path] = None,
    qdrant_store: Optional[QdrantStore] = None,
    embedding_model: Optional[EmbeddingModel] = None,
    save_chunks: bool = True,
) -> IndexingSummary:
    """Indexing pipeline'ni boshidan oxirigacha ishga tushiradi.

    Input:
        settings:        Settings (config/settings.py).
        data_dir:        hujjatlar papkasi; berilmasa — settings.raw_data_dir.
        qdrant_store:    tayyor QdrantStore (test uchun); berilmasa — settings'dan yaratiladi.
        embedding_model: tayyor EmbeddingModel (qayta yuklamaslik uchun); berilmasa — yaratiladi.
        save_chunks:     True bo'lsa, chunk'lar data/processed/chunks.jsonl ga ham yoziladi.
    Output:
        IndexingSummary — haqiqiy natijalar.
    """
    # "a or b" — a bo'sh/None bo'lsa b olinadi: data_dir berilmagan bo'lsa settings'dagi papka
    data_dir = Path(data_dir or settings.raw_data_dir)
    summary = IndexingSummary(data_dir=str(data_dir))

    # --- 1. Discover + Load ------------------------------------------------
    print(f"\n[1/6] Document Loading: {data_dir}")
    load_result = load_directory(data_dir)
    summary.loaded_files = len(load_result.loaded_files)
    summary.failed_files = load_result.failed_files
    summary.unsupported_files = load_result.skipped_files
    summary.discovered_files = summary.loaded_files + len(summary.failed_files) + len(summary.unsupported_files)
    summary.text_sections = len(load_result.documents)
    print(f"      {summary.discovered_files} fayl topildi, {summary.loaded_files} tasi yuklandi, "
          f"{len(summary.failed_files)} tasi xato berdi")

    # --- 2. Metadata -----------------------------------------------------------
    print("[2/6] Metadata")
    # List comprehension: har bir yuklangan Document uchun attach_metadata() chaqiriladi
    documents_with_metadata = [attach_metadata(document, data_dir) for document in load_result.documents]
    print(f"      {len(documents_with_metadata)} ta matn bo'limiga document_id va metadata biriktirildi")

    # --- 3. Clean ------------------------------------------------------------
    print("[3/6] Text Cleaning")
    cleaned_documents = []
    for document in documents_with_metadata:
        cleaned = clean_document(document)  # metadata o'zgarmasdan ko'chiriladi
        if cleaned.text == "":
            summary.empty_sections_skipped += 1  # "+= 1" — qiymatni 1 ga oshirish; bo'sh sahifa chunk'ga aylanmaydi
            continue
        cleaned_documents.append(cleaned)
    print(f"      {len(cleaned_documents)} ta matn bo'limi tozalandi, "
          f"{summary.empty_sections_skipped} tasi bo'sh bo'lgani uchun o'tkazib yuborildi")

    if not cleaned_documents:  # bo'sh ro'yxat False hisoblanadi — "hech narsa qolmadimi?"
        summary.warnings.append("Indexing uchun matn topilmadi. data papkasiga PDF/DOCX/TXT/MD fayl qo'ying.")
        summary.print_report()
        return summary  # return — funksiyadan erta chiqish; keyingi bosqichlar ishlamaydi

    # --- 4. Chunk --------------------------------------------------------------
    print(f"[4/6] Chunking: chunk_size={settings.chunk_size}, overlap={settings.chunk_overlap} token")
    splitter = TokenTextSplitter.from_model_name(  # embedding model'ning o'z tokenizer'i bilan splitter yaratamiz
        settings.embedding_model_name, settings.chunk_size, settings.chunk_overlap
    )
    chunks = splitter.split_documents(cleaned_documents)
    summary.chunks_created = len(chunks)
    print(f"      {len(chunks)} ta chunk yaratildi")
    if save_chunks:
        saved_path = save_chunks_for_inspection(chunks, settings.processed_data_dir)
        print(f"      chunk'lar tekshirish uchun saqlandi: {saved_path}")

    # --- 5. Embed --------------------------------------------------------------
    print(f"[5/6] Embedding Generation: {settings.embedding_model_name}")
    if embedding_model is None:  # tashqaridan berilmagan bo'lsa — o'zimiz yuklaymiz
        embedding_model = EmbeddingModel(settings.embedding_model_name, settings.embedding_batch_size)
    summary.embedding_model = embedding_model.model_name
    summary.vector_dimension = embedding_model.dimension

    # Chunk model ko'ra oladigan uzunlikdan katta bo'lsa — halol ogohlantiramiz (oxiri embedding'ga kirmaydi).
    if settings.chunk_size > embedding_model.max_seq_length:
        summary.warnings.append(
            f"chunk_size ({settings.chunk_size}) model max_seq_length ({embedding_model.max_seq_length}) "
            f"dan katta: har bir chunk'ning {embedding_model.max_seq_length}-tokendan keyingi qismi "
            f"embedding'ga kirmaydi (truncation). TACTIQ_CHUNK_SIZE ni kamaytirishni ko'rib chiqing."
        )

    vectors = embedding_model.embed([chunk.text for chunk in chunks])  # faqat matnlarni model'ga beramiz
    print(f"      vectors.shape = {vectors.shape}  (chunk'lar soni, vector dimension)")

    # --- 6. Store --------------------------------------------------------------
    print(f"[6/6] Qdrant Storage: collection '{settings.qdrant_collection}'")
    created_here = qdrant_store is None  # True — ulanishni shu funksiya ochadi, demak o'zi yopishi kerak
    if created_here:
        client = create_qdrant_client(settings.qdrant_url, settings.qdrant_api_key, settings.qdrant_local_path)
        qdrant_store = QdrantStore(client, settings.qdrant_collection)
    summary.collection_name = qdrant_store.collection_name
    summary.collection_created = qdrant_store.ensure_collection(embedding_model.dimension)
    summary.vectors_stored = qdrant_store.upsert_chunks(chunks, vectors, embedding_model.model_name)
    summary.collection_total_points = qdrant_store.count()
    if created_here:
        qdrant_store.client.close()  # o'zimiz ochgan ulanishni o'zimiz yopamiz

    summary.print_report()
    return summary
