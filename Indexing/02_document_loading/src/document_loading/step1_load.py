"""
2.1 Load — papkadagi PDF, DOCX, TXT, MD fayllarni topadi va matnini Document'ga soladi.

Input:  papka yo'li
Output: LoadResult (o'qilgan Document'lar + xato bergan fayllar)
Keyingi qadam: 2.2 Metadata
"""

from dataclasses import dataclass, field
from pathlib import Path

import pymupdf                          # PDF o'qish
from docx import Document as DocxFile   # DOCX o'qish ("as" — bizning Document bilan chalkashmasin)

from document_loading.step0_document import Document

SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md"}


@dataclass
class LoadResult:
    """Yuklash natijasi: nima o'qildi va nima o'qilmadi."""

    documents: list[Document] = field(default_factory=list)
    loaded_files: list[str] = field(default_factory=list)
    failed_files: dict[str, str] = field(default_factory=dict)   # {fayl: xato matni}
    skipped_files: list[str] = field(default_factory=list)       # qo'llab-quvvatlanmaydigan format


def discover_files(data_dir: Path) -> list[Path]:
    """Papka va ichki papkalardagi barcha fayllarni topadi (yashirin va .meta.json fayllarsiz)."""
    data_dir = Path(data_dir)
    if not data_dir.is_dir():
        raise FileNotFoundError(f"Papka topilmadi: {data_dir}")

    files = [path for path in sorted(data_dir.rglob("*")) if path.is_file()]  # rglob — ichki papkalar bilan
    return [path for path in files if not path.name.startswith(".") and not path.name.endswith(".meta.json")]


def _base_metadata(path: Path, data_dir: Path) -> dict:
    """Fayl haqidagi asosiy ma'lumot (qolganini 2.2 Metadata qo'shadi)."""
    return {
        "source": path.name,                                   # "low_block.txt"
        "source_path": path.relative_to(data_dir).as_posix(),  # papkaga nisbatan yo'l
        "file_type": path.suffix.lower().lstrip("."),          # "txt"
        "page": None,                                          # PDF'da sahifa raqami bo'ladi
    }


def load_text_file(path: Path, data_dir: Path) -> list[Document]:
    """TXT va MD: butun fayl — bitta Document."""
    text = path.read_text(encoding="utf-8")  # utf-8 — "Gündoğan" kabi harflar uchun
    return [Document(text=text, metadata=_base_metadata(path, data_dir))]


def load_pdf_file(path: Path, data_dir: Path) -> list[Document]:
    """PDF: har bir sahifa — alohida Document (sahifa raqami saqlanadi)."""
    documents = []
    with pymupdf.open(path) as pdf:  # with — fayl oxirida avtomatik yopiladi
        for page_number, page in enumerate(pdf, start=1):
            metadata = _base_metadata(path, data_dir)
            metadata["page"] = page_number
            documents.append(Document(text=page.get_text(), metadata=metadata))
    return documents


def load_docx_file(path: Path, data_dir: Path) -> list[Document]:
    """DOCX: paragraph'lar + jadval qatorlari — bitta Document (DOCX'da sahifa raqami yo'q)."""
    docx = DocxFile(str(path))
    parts = [paragraph.text for paragraph in docx.paragraphs]

    for table in docx.tables:  # jadvaldagi ma'lumot ham yo'qolmasin: "a | b | c"
        for row in table.rows:
            cells = [cell.text.strip() for cell in row.cells]
            parts.append(" | ".join(cells))

    text = "\n".join(parts)
    return [Document(text=text, metadata=_base_metadata(path, data_dir))]


# Fayl turi -> uni o'qiydigan funksiya. Yangi format = yangi funksiya + shu yerga bitta qator.
LOADERS = {
    ".txt": load_text_file,
    ".md": load_text_file,
    ".pdf": load_pdf_file,
    ".docx": load_docx_file,
}


def load_file(path: Path, data_dir: Path) -> list[Document]:
    """Bitta faylni formatiga mos funksiya bilan o'qiydi."""
    extension = path.suffix.lower()
    if extension not in LOADERS:
        raise ValueError(f"Qo'llab-quvvatlanmaydigan format: {extension}")
    loader_function = LOADERS[extension]
    return loader_function(path, data_dir)


def load_directory(data_dir: Path) -> LoadResult:
    """Papkadagi barcha fayllarni yuklaydi. Buzilgan fayl pipeline'ni to'xtatmaydi — xato yozib qo'yiladi."""
    data_dir = Path(data_dir)
    result = LoadResult()

    for path in discover_files(data_dir):
        relative_path = path.relative_to(data_dir).as_posix()

        if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            result.skipped_files.append(relative_path)
            continue

        try:
            documents = load_file(path, data_dir)
        except Exception as error:  # buzilgan fayl: xatoni yozamiz va keyingi faylga o'tamiz
            result.failed_files[relative_path] = f"{type(error).__name__}: {error}"
            continue

        result.documents.extend(documents)
        result.loaded_files.append(relative_path)

    return result
