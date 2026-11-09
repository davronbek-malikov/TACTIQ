"""
2.2 Metadata — har bir Document'ga "pasport" beradi: document_id, source, page, topic ...

Fayldan bilinadigan narsalar (nomi, turi, sahifasi) — avtomatik.
topic, language, match_id ... — faqat odam yozgan sidecar'dan (<fayl>.meta.json).
Sidecar bo'lmasa — None. Metadata'ni o'ylab topmaymiz.

Keyingi qadam: 2.3 Text Cleaning
"""

import json
import uuid
from pathlib import Path
from typing import Optional

from document_loading.step0_document import Document

# uuid5 — bir xil nom uchun HAR DOIM bir xil ID (uuid4 esa har safar yangi).
# Shu sababli qayta index qilganda dublikat bo'lmaydi. Bu qiymatni o'zgartirmang.
TACTIQ_NAMESPACE = uuid.UUID("8c6b1f0e-2d4a-4b7e-9f3c-5a1d2e3f4b6c")

# Sidecar'dan olinadigan maydonlar
OPTIONAL_FIELDS = ["document_type", "topic", "language", "match_id", "team_id", "player_id"]


def make_document_id(source_path: str) -> str:
    """Fayl yo'lidan barqaror ID: bir xil yo'l -> bir xil ID (PDF sahifalari ham bitta ID)."""
    return str(uuid.uuid5(TACTIQ_NAMESPACE, f"document:{source_path}"))


def read_sidecar_metadata(file_path: Path) -> dict:
    """<fayl>.meta.json ni o'qiydi. Yo'q bo'lsa — {}."""
    sidecar_path = file_path.with_name(file_path.name + ".meta.json")
    if not sidecar_path.exists():
        return {}

    with sidecar_path.open(encoding="utf-8") as file:
        data = json.load(file)

    return {key: data[key] for key in OPTIONAL_FIELDS if key in data}  # faqat ruxsat etilgan kalitlar


def build_metadata(document: Document, data_dir: Optional[Path] = None) -> dict:
    """Har doim bir xil 11 ta kalitli metadata yasaydi."""
    source_path = document.metadata["source_path"]

    metadata = {
        "document_id": make_document_id(source_path),
        "source": document.metadata["source"],
        "source_path": source_path,
        "file_type": document.metadata["file_type"],
        "page": document.metadata.get("page"),
    }

    for key in OPTIONAL_FIELDS:  # default: None (noma'lum)
        metadata[key] = None

    if data_dir is not None:
        sidecar = read_sidecar_metadata(Path(data_dir) / source_path)
        metadata.update(sidecar)  # sidecar'dagi qiymatlar None'lar ustiga yoziladi

    return metadata


def attach_metadata(document: Document, data_dir: Optional[Path] = None) -> Document:
    """Matnni o'zgartirmasdan, metadata'si to'ldirilgan YANGI Document qaytaradi."""
    return Document(text=document.text, metadata=build_metadata(document, data_dir))
