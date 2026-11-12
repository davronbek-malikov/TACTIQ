"""
documents — 01_documents papkasidagi fayllar bilan ishlash: ro'yxat, tafsilot, yuklash, metadata.

Ikki manba:
    sample_docs  — dars uchun namunalar (faqat o'qish)
    my_documents — foydalanuvchi yuklagan haqiqiy hujjatlar (git'ga tushmaydi)

Fayllarni o'qish va metadata yasash — Indexing'dagi funksiyalar bilan (qayta yozilmagan).
"""

import json
import re
from collections import Counter
from pathlib import Path

from document_loading import (
    OPTIONAL_FIELDS,
    SUPPORTED_EXTENSIONS,
    attach_metadata,
    clean_document,
    discover_files,
    load_file,
    make_document_id,
    read_sidecar_metadata,
)
from qdrant_client.models import FieldCondition, Filter, MatchValue

import core

DOCUMENTS_DIR = core.PROJECT_ROOT / "Indexing" / "01_documents"
SOURCES = {"sample_docs": DOCUMENTS_DIR / "sample_docs", "my_documents": DOCUMENTS_DIR / "my_documents"}
EDITABLE_SOURCES = {"my_documents"}         # namunalar o'zgartirilmaydi
MAX_UPLOAD_BYTES = 20 * 1024 * 1024         # 20 MB
SAFE_NAME = re.compile(r"^[\w\-. ()]+$")    # harf, raqam, _ - . bo'sh joy, qavslar


def source_dir(source: str) -> Path:
    if source not in SOURCES:
        raise ValueError(f"Noma'lum manba: {source}")
    return SOURCES[source]


def resolve_file(source: str, filename: str) -> Path:
    """Fayl yo'lini xavfsiz topadi: faqat manba papkasi ichidagi qo'llab-quvvatlanadigan fayl."""
    folder = source_dir(source).resolve()
    path = (folder / filename).resolve()
    if path.parent != folder or path.suffix.lower() not in SUPPORTED_EXTENSIONS or not path.is_file():
        raise FileNotFoundError(f"Hujjat topilmadi: {source}/{filename}")
    return path


def chunk_counts(collection: str = None) -> Counter:
    """Qdrant'dagi har bir document_id uchun chunk'lar soni (Qdrant ishlamasa — bo'sh)."""
    counts = Counter()
    try:
        with core.qdrant_lock:
            store = core.get_store(collection)
            if not store.client.collection_exists(store.collection_name):
                return counts
            offset = None
            while True:
                points, offset = store.client.scroll(
                    store.collection_name, limit=256, offset=offset,
                    with_payload=["document_id"], with_vectors=False,
                )
                counts.update(point.payload.get("document_id") for point in points)
                if offset is None:
                    break
    except Exception:
        pass
    return counts


def list_documents(collection: str = None) -> list[dict]:
    """Ikkala manbadagi hujjatlar: nomi, turi, metadata, Qdrant'dagi chunk soni."""
    counts = chunk_counts(collection)
    rows = []
    for source, folder in SOURCES.items():
        if not folder.is_dir():
            continue
        for path in discover_files(folder):
            if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
                continue
            relative = path.relative_to(folder).as_posix()
            document_id = make_document_id(relative)
            sidecar = read_sidecar_metadata(path)
            rows.append({
                "source": source,
                "filename": relative,
                "document_id": document_id,
                "file_type": path.suffix.lower().lstrip("."),
                "size_bytes": path.stat().st_size,
                "metadata": {key: sidecar.get(key) for key in OPTIONAL_FIELDS},
                "chunks": counts.get(document_id, 0),
                "indexed": counts.get(document_id, 0) > 0,
                "editable": source in EDITABLE_SOURCES,
            })
    return rows


def document_detail(source: str, filename: str, collection: str = None) -> dict:
    """Bitta hujjat: metadata, sahifalar bo'yicha matn namunasi va Qdrant'dagi chunk'lar."""
    path = resolve_file(source, filename)
    folder = source_dir(source)
    pages = []
    metadata = {}
    for document in load_file(path, folder):
        prepared = clean_document(attach_metadata(document, folder))  # Indexing'dagi 2.2 + 2.3
        metadata = {k: v for k, v in prepared.metadata.items() if k != "page"}
        pages.append({"page": prepared.metadata.get("page"), "characters": len(prepared.text),
                      "preview": prepared.text[:1200]})

    chunks = []
    try:
        with core.qdrant_lock:
            store = core.get_store(collection)
            if store.client.collection_exists(store.collection_name):
                points, _ = store.client.scroll(
                    store.collection_name, limit=500, with_payload=True, with_vectors=False,
                    scroll_filter=Filter(must=[FieldCondition(key="document_id", match=MatchValue(value=metadata["document_id"]))]),
                )
                chunks = sorted((p.payload for p in points), key=lambda p: (p.get("page") or 0, p.get("chunk_index") or 0))
    except Exception:
        chunks = []

    return {
        "source": source,
        "filename": filename,
        "metadata": metadata,
        "pages": pages,
        "chunks": [{"chunk_index": c.get("chunk_index"), "page": c.get("page"), "token_count": c.get("token_count"),
                    "text": c.get("chunk_text", "")} for c in chunks],
        "embedding_model": chunks[0].get("embedding_model") if chunks else None,
        "editable": source in EDITABLE_SOURCES,
    }


def validate_upload_name(filename: str) -> str:
    """Faqat oddiy fayl nomi va qo'llab-quvvatlanadigan format."""
    name = Path(filename or "").name
    if not name or name.startswith(".") or not SAFE_NAME.match(name):
        raise ValueError("Fayl nomi noto'g'ri. Faqat harf, raqam, '-', '_', '.' ishlating.")
    if Path(name).suffix.lower() not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Format qo'llab-quvvatlanmaydi. Ruxsat: {', '.join(sorted(SUPPORTED_EXTENSIONS))}")
    if (SOURCES["sample_docs"] / name).exists():
        raise ValueError("Bu nom namunaviy hujjat bilan bir xil. Boshqa nom bering.")
    return name


def save_upload(filename: str, content: bytes, metadata: dict, overwrite: bool = False) -> dict:
    """Faylni my_documents'ga saqlaydi; metadata berilsa — sidecar ham yoziladi."""
    name = validate_upload_name(filename)
    if len(content) == 0:
        raise ValueError("Fayl bo'sh.")
    if len(content) > MAX_UPLOAD_BYTES:
        raise ValueError("Fayl juda katta (maksimum 20 MB).")
    folder = SOURCES["my_documents"]
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / name
    if path.exists() and not overwrite:
        raise FileExistsError(f"'{name}' allaqachon mavjud.")
    path.write_bytes(content)
    if any(metadata.values()):
        write_sidecar(path, metadata)
    return {"source": "my_documents", "filename": name, "document_id": make_document_id(name)}


def write_sidecar(path: Path, metadata: dict) -> None:
    clean = {key: (metadata.get(key) or None) for key in OPTIONAL_FIELDS}
    path.with_name(path.name + ".meta.json").write_text(json.dumps(clean, indent=2) + "\n", encoding="utf-8")


def update_metadata(source: str, filename: str, metadata: dict) -> dict:
    """Sidecar'ni yangilaydi. Qdrant'ga ta'sir qilishi uchun keyin qayta index qilish kerak."""
    if source not in EDITABLE_SOURCES:
        raise PermissionError("Namunaviy hujjatlar metadata'si o'zgartirilmaydi.")
    path = resolve_file(source, filename)
    write_sidecar(path, metadata)
    return {key: (metadata.get(key) or None) for key in OPTIONAL_FIELDS}


def delete_document(source: str, filename: str) -> None:
    """Faylni va uning Qdrant'dagi chunk'larini o'chiradi (faqat my_documents)."""
    if source not in EDITABLE_SOURCES:
        raise PermissionError("Namunaviy hujjatlar o'chirilmaydi.")
    path = resolve_file(source, filename)
    document_id = make_document_id(path.relative_to(source_dir(source)).as_posix())
    with core.qdrant_lock:
        store = core.get_store()
        if store.client.collection_exists(store.collection_name):
            store.delete_document(document_id)
    path.unlink()
    path.with_name(path.name + ".meta.json").unlink(missing_ok=True)
