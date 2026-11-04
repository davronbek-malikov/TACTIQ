"""
Document Loading — 1-bosqich

Bu modul `data/raw/` papkasidagi (va uning ichki papkalaridagi) PDF, DOCX, TXT va Markdown
fayllarni topadi, ulardan matn ajratib oladi va har birini Document obyektiga aylantiradi.

Bu modul matnni TOZALAMAYDI va BO'LMAYDI — bu keyingi bosqichlarning vazifasi.
Har bir modulning vazifasi bitta bo'lsa, uni alohida test qilish va almashtirish oson.

Input:  papka yo'li (Path)
Output: LoadResult — muvaffaqiyatli o'qilgan Document'lar + xato bergan fayllar ro'yxati

Keyingi bosqich: Text Cleaning.
"""

from dataclasses import dataclass, field
from pathlib import Path

import pymupdf  # PyMuPDF — PDF fayllardan matn o'qish uchun
from docx import Document as DocxFile  # python-docx — Word (.docx) fayllar uchun

from tactiq.indexing.document_loading.document import Document

# Qo'llab-quvvatlanadigan fayl kengaytmalari (extension).
SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md"}


@dataclass
class LoadResult:
    """Yuklash natijasi: nima o'qildi, nima o'qilmadi.

    Pipeline oxirida haqiqiy statistikani (nechta fayl xato berdi va h.k.) ko'rsatish uchun kerak.
    """

    documents: list[Document] = field(default_factory=list)
    loaded_files: list[str] = field(default_factory=list)
    failed_files: dict[str, str] = field(default_factory=dict)  # {fayl yo'li: xato matni}
    skipped_files: list[str] = field(default_factory=list)      # qo'llab-quvvatlanmaydigan format


# ---------------------------------------------------------------------------
# 1. Fayllarni topish (discovery)
# ---------------------------------------------------------------------------

def discover_files(data_dir: Path) -> list[Path]:
    """Papka ichidagi BARCHA fayllarni rekursiv (ichki papkalar bilan) topadi.

    rglob("*") — "recursive glob": papka va uning barcha ichki papkalaridagi har bir element.
    sorted() — natija har safar bir xil tartibda bo'lishi uchun (takrorlanuvchanlik muhim).

    Input:  data_dir — qidiriladigan papka.
    Output: fayllar ro'yxati (papkalar emas). Qo'llab-quvvatlanmaydiganlari ham kiradi —
            ularni load_directory() alohida hisoblaydi.
    """
    data_dir = Path(data_dir)
    if not data_dir.is_dir():
        raise FileNotFoundError(f"Papka topilmadi: {data_dir}")

    # List comprehension — sikl + shart + yangi ro'yxat yaratishni bitta qatorda yozish usuli.
    # Quyidagi qator shunga teng:
    #     files = []
    #     for path in sorted(data_dir.rglob("*")):
    #         if path.is_file():
    #             files.append(path)
    files = [path for path in sorted(data_dir.rglob("*")) if path.is_file()]

    # Yashirin fayllarni (.gitkeep, .DS_Store) va metadata "sidecar" fayllarini o'tkazib yuboramiz.
    return [path for path in files if not path.name.startswith(".") and not path.name.endswith(".meta.json")]


# ---------------------------------------------------------------------------
# 2. Har bir format uchun alohida loader funksiya
# ---------------------------------------------------------------------------

def _base_metadata(path: Path, data_dir: Path) -> dict:
    """Fayl haqidagi asosiy (source) ma'lumot. Boshqa metadata'ni Metadata bosqichi qo'shadi."""
    return {
        "source": path.name,                                   # fayl nomi: "high_pressing.pdf"
        "source_path": path.relative_to(data_dir).as_posix(),  # "tactics/high_pressing.pdf"
        "file_type": path.suffix.lower().lstrip("."),          # "pdf"
        "page": None,
    }


def load_text_file(path: Path, data_dir: Path) -> list[Document]:
    """TXT va Markdown fayllarni o'qiydi (Python'ning o'zi yetarli, kutubxona kerak emas).

    encoding="utf-8" — "Gündoğan", "Ødegaard" kabi lotin bo'lmagan harflar to'g'ri o'qilishi uchun.
    """
    text = path.read_text(encoding="utf-8")
    return [Document(text=text, metadata=_base_metadata(path, data_dir))]


def load_pdf_file(path: Path, data_dir: Path) -> list[Document]:
    """PDF faylni o'qiydi: har bir sahifa — alohida Document (sahifa raqami saqlanadi).

    `with ... as pdf:` — context manager. Blok tugaganda (hatto xato bo'lsa ham)
    fayl avtomatik yopiladi. Aks holda ochiq qolgan fayllar xotirani band qiladi va
    Windows'da faylni o'chirib/ko'chirib bo'lmay qoladi.
    """
    documents = []
    with pymupdf.open(path) as pdf:
        # enumerate(..., start=1) — sahifalarni 1 dan boshlab raqamlaydi (odamlar shunday sanaydi).
        for page_number, page in enumerate(pdf, start=1):
            metadata = _base_metadata(path, data_dir)
            metadata["page"] = page_number
            documents.append(Document(text=page.get_text(), metadata=metadata))
    return documents


def load_docx_file(path: Path, data_dir: Path) -> list[Document]:
    """DOCX faylni o'qiydi: paragraph'lar va jadval (table) qatorlari bitta matnga yig'iladi.

    Eslatma: DOCX'da "sahifa" tushunchasi faylning o'zida saqlanmaydi (u ekranda hisoblanadi),
    shuning uchun page = None bo'lib qoladi.
    """
    docx = DocxFile(str(path))
    parts = [paragraph.text for paragraph in docx.paragraphs]

    # Jadvallardagi ma'lumotni ham yo'qotmaslik uchun har bir qatorni "a | b | c" ko'rinishida qo'shamiz.
    for table in docx.tables:
        for row in table.rows:
            cells = [cell.text.strip() for cell in row.cells]
            parts.append(" | ".join(cells))

    text = "\n".join(parts)
    return [Document(text=text, metadata=_base_metadata(path, data_dir))]


# Fayl kengaytmasi -> qaysi funksiya o'qiydi.
# Yangi format qo'shish uchun: yangi load_..._file() funksiyasini yozib, shu yerga bitta qator qo'shamiz.
LOADERS = {
    ".txt": load_text_file,
    ".md": load_text_file,
    ".pdf": load_pdf_file,
    ".docx": load_docx_file,
}


def load_file(path: Path, data_dir: Path) -> list[Document]:
    """Bitta faylni formatiga mos loader bilan o'qiydi.

    Qo'llab-quvvatlanmaydigan format uchun ValueError ko'taradi (raise).
    """
    extension = path.suffix.lower()
    if extension not in LOADERS:
        raise ValueError(f"Qo'llab-quvvatlanmaydigan format: {extension}")
    loader_function = LOADERS[extension]
    return loader_function(path, data_dir)


# ---------------------------------------------------------------------------
# 3. Butun papkani yuklash
# ---------------------------------------------------------------------------

def load_directory(data_dir: Path) -> LoadResult:
    """Papkadagi barcha qo'llab-quvvatlanadigan fayllarni yuklaydi.

    Muhim: bitta buzilgan fayl butun pipeline'ni to'xtatib qo'ymasligi kerak.
    Shuning uchun har bir fayl `try / except` ichida o'qiladi.

    Exception handling:
        try:    — xato chiqishi mumkin bo'lgan kod
        except: — xato chiqsa, dastur to'xtamaydi, shu blok ishlaydi
    Biz xatoni "yutib yubormaymiz": u failed_files ro'yxatiga yoziladi va oxirida ko'rsatiladi.

    Input:  data_dir — `data/raw/` yoki boshqa papka.
    Output: LoadResult.
    """
    data_dir = Path(data_dir)
    result = LoadResult()

    for path in discover_files(data_dir):
        relative_path = path.relative_to(data_dir).as_posix()

        if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            result.skipped_files.append(relative_path)
            continue

        try:
            documents = load_file(path, data_dir)
        except Exception as error:  # buzilgan PDF, noto'g'ri encoding va h.k.
            result.failed_files[relative_path] = f"{type(error).__name__}: {error}"
            continue

        result.documents.extend(documents)
        result.loaded_files.append(relative_path)

    return result
