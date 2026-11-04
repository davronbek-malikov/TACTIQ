"""1-bosqich: Document loading — PDF, TXT/MD, DOCX fayllardan matnni chiqarib olish.

Har bir loader bir xil narsani qaytaradi: list[Document].
Shu sababli keyingi bosqichlar (chunking, embedding) fayl formatini bilishi shart emas.
"""

from dataclasses import dataclass, field
from pathlib import Path

from docx import Document as DocxFile
from pypdf import PdfReader

from config import DATA_DIR
from indexing_pipeline.data_loading.metadata import build_metadata


@dataclass
class Document:
    text: str
    metadata: dict = field(default_factory=dict)


def load_txt(path: Path, data_dir: Path) -> list[Document]:
    text = path.read_text(encoding="utf-8")
    return [Document(text=text, metadata=build_metadata(path, data_dir))]


def load_pdf(path: Path, data_dir: Path) -> list[Document]:
    """PDF -> har bir sahifa alohida Document (sahifa raqami metadata'da qoladi)."""
    reader = PdfReader(path)
    documents = []
    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        if text.strip():  # bo'sh (masalan, faqat rasm) sahifalarni tashlab ketamiz
            documents.append(
                Document(text=text, metadata=build_metadata(path, data_dir, page=page_number))
            )
    return documents


def load_docx(path: Path, data_dir: Path) -> list[Document]:
    """DOCX -> paragraph'lar va jadvallar bitta matnga yig'iladi."""
    docx = DocxFile(path)
    parts = [p.text for p in docx.paragraphs if p.text.strip()]
    for table in docx.tables:  # narxlar ko'pincha jadvalda bo'ladi
        for row in table.rows:
            parts.append(" | ".join(cell.text.strip() for cell in row.cells))
    return [Document(text="\n".join(parts), metadata=build_metadata(path, data_dir))]


# Fayl kengaytmasi -> qaysi loader. Yangi format qo'shish = shu yerga bitta qator.
LOADERS = {
    ".txt": load_txt,
    ".md": load_txt,
    ".pdf": load_pdf,
    ".docx": load_docx,
}


def load_directory(data_dir: Path = DATA_DIR) -> list[Document]:
    """data_dir ichidagi barcha qo'llab-quvvatlanadigan fayllarni (sub-papkalar bilan) yuklaydi."""
    data_dir = Path(data_dir)
    documents = []
    for path in sorted(data_dir.rglob("*")):
        loader = LOADERS.get(path.suffix.lower())
        if loader is None or not path.is_file():
            continue
        loaded = loader(path, data_dir)
        print(f"  [load] {path.relative_to(data_dir)} -> {len(loaded)} document")
        documents.extend(loaded)
    return documents
