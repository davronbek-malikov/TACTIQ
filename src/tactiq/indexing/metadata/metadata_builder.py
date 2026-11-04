"""
Metadata — 3-bosqich

Metadata — "matn haqidagi ma'lumot": u qaysi fayldan, qaysi sahifadan kelgani,
qanday hujjat turi, qaysi mavzu, qaysi til va (bo'lsa) qaysi o'yin / jamoa / o'yinchiga tegishli.

Nima uchun kerak?
  * Citation: javob ostida "manba: high_pressing.pdf, 2-sahifa" deb ko'rsatish.
  * Metadata filtering: kelajakda "faqat match_id = X bo'yicha hujjatlardan qidir".
  * Provenance: har bir dalil (evidence) qayerdan kelganini kuzatish — TACTIQ'ning asosiy tamoyili.

Qoidamiz: metadata'ni O'YLAB TOPMAYMIZ.
  * Fayldan aniq bilinadigan narsalar (nomi, turi, sahifasi) — avtomatik.
  * document_type, topic, language, match_id, team_id, player_id — faqat odam yozib bergan
    "sidecar" fayldan olinadi: `high_pressing.pdf` yonida `high_pressing.pdf.meta.json`.
  * Sidecar bo'lmasa — None ("noma'lum"). None — to'g'ri javob, taxmin esa xato bo'lishi mumkin.

Bu modul Text Cleaning'dan ALOHIDA: tozalash matnni o'zgartiradi, metadata esa matnga tegmaydi.

Input:  tozalangan Document
Output: to'liq metadata'ga ega Document

Keyingi bosqich: Chunking.
"""

import json
import uuid
from pathlib import Path
from typing import Optional

from tactiq.indexing.document_loading import Document

# UUID (Universally Unique Identifier) — 128-bitli noyob identifikator,
# masalan "3f2b8c1e-5d7a-5e2b-9c4d-1a2b3c4d5e6f".
# uuid4() — tasodifiy: har chaqiruvda YANGI qiymat.
# uuid5(namespace, name) — deterministik: bir xil "name" uchun HAR DOIM bir xil UUID.
# Biz uuid5 ishlatamiz: bitta fayl qayta-qayta ingest qilinganda ham document_id o'zgarmaydi,
# shuning uchun Qdrant'da dublikatlar paydo bo'lmaydi.
# Bu namespace — TACTIQ uchun bir marta tanlangan doimiy qiymat. Uni o'zgartirmang:
# o'zgarsa, barcha ID'lar o'zgaradi va eski ma'lumotlar dublikatga aylanadi.
TACTIQ_NAMESPACE = uuid.UUID("8c6b1f0e-2d4a-4b7e-9f3c-5a1d2e3f4b6c")

# Sidecar faylda yozish mumkin bo'lgan maydonlar. Boshqa kalitlar e'tiborga olinmaydi.
OPTIONAL_FIELDS = ["document_type", "topic", "language", "match_id", "team_id", "player_id"]


def make_document_id(source_path: str) -> str:
    """Fayl yo'lidan barqaror (stable) document_id yasaydi.

    Input:  source_path — data papkasiga nisbatan yo'l, masalan "tactics/high_pressing.pdf".
    Output: UUID string. Bir xil yo'l -> har doim bir xil ID.

    Eslatma: PDF'ning barcha sahifalari bitta document_id'ga ega (ular bitta hujjat).
    """
    return str(uuid.uuid5(TACTIQ_NAMESPACE, f"document:{source_path}"))


def read_sidecar_metadata(file_path: Path) -> dict:
    """`<fayl>.meta.json` sidecar faylini o'qiydi (agar mavjud bo'lsa).

    Input:  hujjat faylining to'liq yo'li.
    Output: faqat OPTIONAL_FIELDS'dagi kalitlardan iborat dict. Sidecar bo'lmasa — {}.
    """
    sidecar_path = file_path.with_name(file_path.name + ".meta.json")
    if not sidecar_path.exists():
        return {}

    with sidecar_path.open(encoding="utf-8") as file:
        data = json.load(file)

    return {key: data[key] for key in OPTIONAL_FIELDS if key in data}


def build_metadata(document: Document, data_dir: Optional[Path] = None) -> dict:
    """Document uchun to'liq, bir xil tuzilmadagi metadata dict yaratadi.

    Input:
        document: Document Loading bergan source ma'lumotiga ega Document.
        data_dir: sidecar fayllarni topish uchun data papkasi (None bo'lsa — sidecar o'qilmaydi).
    Output:
        {"document_id", "source", "source_path", "file_type", "page",
         "document_type", "topic", "language", "match_id", "team_id", "player_id"}
    """
    source_path = document.metadata["source_path"]

    metadata = {
        "document_id": make_document_id(source_path),
        "source": document.metadata["source"],
        "source_path": source_path,
        "file_type": document.metadata["file_type"],
        "page": document.metadata.get("page"),
    }

    # Noma'lum maydonlar uchun default: None (to'qib chiqarilgan qiymat emas).
    for key in OPTIONAL_FIELDS:
        metadata[key] = None

    if data_dir is not None:
        sidecar = read_sidecar_metadata(Path(data_dir) / source_path)
        metadata.update(sidecar)

    return metadata


def attach_metadata(document: Document, data_dir: Optional[Path] = None) -> Document:
    """Matnni o'zgartirmasdan, Document'ga to'liq metadata biriktiradi."""
    return Document(text=document.text, metadata=build_metadata(document, data_dir))
