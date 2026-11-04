"""
Document Loading — 1-bosqich

Bu modul `data/raw/` papkasidagi (va uning ichki papkalaridagi) PDF, DOCX, TXT va Markdown
fayllarni topadi, ulardan matn ajratib oladi va har birini Document obyektiga aylantiradi.

Bu modul matnni TOZALAMAYDI va BO'LMAYDI — bu keyingi bosqichlarning vazifasi.
Har bir modulning vazifasi bitta bo'lsa, uni alohida test qilish va almashtirish oson.

Input:  papka yo'li (Path)
Output: LoadResult — muvaffaqiyatli o'qilgan Document'lar + xato bergan fayllar ro'yxati

Keyingi bosqich: Metadata.
"""

from dataclasses import dataclass, field  # dataclass — ma'lumot saqlovchi class'ni qisqa yozish; field — atribut sozlamasi
from pathlib import Path  # pathlib — fayl va papka yo'llari bilan ishlash (Windows va Linux'da bir xil ishlaydi)

import pymupdf  # PyMuPDF — PDF fayllarni ochish va sahifalardan matn ajratib olish kutubxonasi (pip install pymupdf)
from docx import Document as DocxFile  # python-docx — Word (.docx) fayllarni o'qish kutubxonasi.
#                                        "as DocxFile" — boshqa nom (alias) beramiz, chunki bizning
#                                        o'z Document class'imiz bor; ikki xil "Document" chalkashmasin.

from indexing.step1_document_loading.document import Document  # o'zimizning Document dataclass'imiz (document.py)

# Qo'llab-quvvatlanadigan fayl kengaytmalari (extension).
# {...} — set (to'plam): takrorlanmaydigan elementlar; "x in set" tekshiruvi juda tez.
SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md"}


@dataclass
class LoadResult:
    """Yuklash natijasi: nima o'qildi, nima o'qilmadi.

    Pipeline oxirida haqiqiy statistikani (nechta fayl xato berdi va h.k.) ko'rsatish uchun kerak.
    """

    documents: list[Document] = field(default_factory=list)       # list[Document] — Document'lar ro'yxati
    loaded_files: list[str] = field(default_factory=list)         # muvaffaqiyatli o'qilgan fayllar yo'llari
    failed_files: dict[str, str] = field(default_factory=dict)    # {fayl yo'li: xato matni}
    skipped_files: list[str] = field(default_factory=list)        # qo'llab-quvvatlanmaydigan format (.png, .mp4 ...)


# ---------------------------------------------------------------------------
# 1. Fayllarni topish (discovery)
# ---------------------------------------------------------------------------

def discover_files(data_dir: Path) -> list[Path]:  # "-> list[Path]" — funksiya Path'lar ro'yxatini qaytaradi (type hint)
    """Papka ichidagi BARCHA fayllarni rekursiv (ichki papkalar bilan) topadi.

    Input:  data_dir — qidiriladigan papka.
    Output: fayllar ro'yxati (papkalar emas). Qo'llab-quvvatlanmaydiganlari ham kiradi —
            ularni load_directory() alohida hisoblaydi.
    """
    data_dir = Path(data_dir)  # string berilgan bo'lsa ham Path obyektiga aylantiramiz
    if not data_dir.is_dir():  # .is_dir() — bu yo'l mavjud papkami?
        raise FileNotFoundError(f"Papka topilmadi: {data_dir}")  # raise — xato (exception) chiqarib, funksiyani to'xtatadi
        #                                                          f"...{x}" — f-string: {} ichidagi qiymat matnga qo'yiladi

    # rglob("*") — "recursive glob": papka va uning barcha ichki papkalaridagi har bir element.
    # sorted()   — natija har safar bir xil tartibda bo'lishi uchun (takrorlanuvchanlik muhim).
    #
    # List comprehension — sikl + shart + yangi ro'yxat yaratishni bitta qatorda yozish usuli.
    # Quyidagi qator shunga teng:
    #     files = []
    #     for path in sorted(data_dir.rglob("*")):
    #         if path.is_file():
    #             files.append(path)
    files = [path for path in sorted(data_dir.rglob("*")) if path.is_file()]

    # Yashirin fayllarni (.gitkeep, .DS_Store) va metadata "sidecar" fayllarini (.meta.json) o'tkazib yuboramiz.
    # .startswith(".") — nom nuqta bilan boshlanadimi; .endswith(...) — shu bilan tugaydimi.
    return [path for path in files if not path.name.startswith(".") and not path.name.endswith(".meta.json")]


# ---------------------------------------------------------------------------
# 2. Har bir format uchun alohida loader funksiya
# ---------------------------------------------------------------------------

def _base_metadata(path: Path, data_dir: Path) -> dict:  # "_" bilan boshlangan nom — "ichki yordamchi funksiya" degan kelishuv
    """Fayl haqidagi asosiy (source) ma'lumot. Boshqa metadata'ni Metadata bosqichi qo'shadi."""
    return {
        "source": path.name,                                   # .name — faqat fayl nomi: "high_pressing.pdf"
        "source_path": path.relative_to(data_dir).as_posix(),  # data papkasiga nisbatan yo'l, "/" bilan: "tactics/high_pressing.pdf"
        "file_type": path.suffix.lower().lstrip("."),          # .suffix — ".PDF" -> .lower() ".pdf" -> .lstrip(".") "pdf"
        "page": None,                                          # None — "qiymat yo'q". PDF loader buni sahifa raqami bilan almashtiradi
    }


def load_text_file(path: Path, data_dir: Path) -> list[Document]:
    """TXT va Markdown fayllarni o'qiydi (Python'ning o'zi yetarli, kutubxona kerak emas)."""
    # encoding="utf-8" — "Gündoğan", "Ødegaard" kabi lotin bo'lmagan harflar to'g'ri o'qilishi uchun.
    text = path.read_text(encoding="utf-8")  # .read_text() — faylni ochadi, butun matnni o'qiydi va yopadi
    return [Document(text=text, metadata=_base_metadata(path, data_dir))]  # [ ... ] — bitta elementli ro'yxat


def load_pdf_file(path: Path, data_dir: Path) -> list[Document]:
    """PDF faylni o'qiydi: har bir sahifa — alohida Document (sahifa raqami saqlanadi)."""
    documents = []  # bo'sh ro'yxat — sahifalar shu yerga qo'shiladi

    # `with ... as pdf:` — context manager. Blok tugaganda (hatto xato bo'lsa ham)
    # fayl avtomatik yopiladi. Aks holda ochiq qolgan fayllar xotirani band qiladi va
    # Windows'da faylni o'chirib/ko'chirib bo'lmay qoladi.
    with pymupdf.open(path) as pdf:  # pymupdf.open() — PDF faylni ochadi; pdf obyekti sahifalar ketma-ketligi
        # enumerate(..., start=1) — har bir elementga tartib raqam beradi, 1 dan boshlab (odamlar shunday sanaydi).
        for page_number, page in enumerate(pdf, start=1):
            metadata = _base_metadata(path, data_dir)
            metadata["page"] = page_number  # dict'dagi "page" kalitining qiymatini o'zgartiramiz
            # page.get_text() — PyMuPDF metodi: sahifadagi matnni string sifatida qaytaradi
            documents.append(Document(text=page.get_text(), metadata=metadata))  # .append() — ro'yxat oxiriga qo'shadi
    return documents


def load_docx_file(path: Path, data_dir: Path) -> list[Document]:
    """DOCX faylni o'qiydi: paragraph'lar va jadval (table) qatorlari bitta matnga yig'iladi.

    Eslatma: DOCX'da "sahifa" tushunchasi faylning o'zida saqlanmaydi (u ekranda hisoblanadi),
    shuning uchun page = None bo'lib qoladi.
    """
    docx = DocxFile(str(path))  # python-docx faylni ochadi; str(path) — Path'ni oddiy matnga aylantiramiz
    parts = [paragraph.text for paragraph in docx.paragraphs]  # .paragraphs — hujjatdagi barcha paragraph'lar

    # Jadvallardagi ma'lumotni ham yo'qotmaslik uchun har bir qatorni "a | b | c" ko'rinishida qo'shamiz.
    for table in docx.tables:            # .tables — hujjatdagi barcha jadvallar
        for row in table.rows:           # .rows — jadval qatorlari
            cells = [cell.text.strip() for cell in row.cells]  # .strip() — boshi va oxiridagi bo'sh joylarni olib tashlaydi
            parts.append(" | ".join(cells))  # " | ".join([...]) — ro'yxat elementlarini " | " bilan bitta matnga ulaydi

    text = "\n".join(parts)  # "\n" — yangi qator belgisi; har bir bo'lak alohida qatorda
    return [Document(text=text, metadata=_base_metadata(path, data_dir))]


# Fayl kengaytmasi -> qaysi funksiya o'qiydi.
# Python'da funksiya ham qiymat: uni dict ichida saqlab, keyinroq chaqirish mumkin (qavssiz yozilgan!).
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
    extension = path.suffix.lower()  # ".PDF" -> ".pdf"
    if extension not in LOADERS:     # "not in" — dict'da bunday kalit yo'qmi?
        raise ValueError(f"Qo'llab-quvvatlanmaydigan format: {extension}")  # ValueError — "noto'g'ri qiymat" xatosi
    loader_function = LOADERS[extension]   # dict'dan mos funksiyani olamiz (hali chaqirmadik)
    return loader_function(path, data_dir)  # endi chaqiramiz: masalan load_pdf_file(path, data_dir)


# ---------------------------------------------------------------------------
# 3. Butun papkani yuklash
# ---------------------------------------------------------------------------

def load_directory(data_dir: Path) -> LoadResult:
    """Papkadagi barcha qo'llab-quvvatlanadigan fayllarni yuklaydi.

    Muhim: bitta buzilgan fayl butun pipeline'ni to'xtatib qo'ymasligi kerak.
    Shuning uchun har bir fayl `try / except` ichida o'qiladi.

    Input:  data_dir — `data/raw/` yoki boshqa papka.
    Output: LoadResult.
    """
    data_dir = Path(data_dir)
    result = LoadResult()  # bo'sh natija obyekti; dataclass yaratgan __init__ barcha ro'yxatlarni bo'sh qiladi

    for path in discover_files(data_dir):
        relative_path = path.relative_to(data_dir).as_posix()  # hisobotda qisqa yo'l ko'rsatish uchun

        if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            result.skipped_files.append(relative_path)
            continue  # continue — sikldagi qolgan qadamlarni o'tkazib, keyingi faylga o'tadi

        # Exception handling:
        #   try:    — xato chiqishi mumkin bo'lgan kod
        #   except: — xato chiqsa, dastur to'xtamaydi, shu blok ishlaydi
        # Biz xatoni "yutib yubormaymiz": u failed_files ro'yxatiga yoziladi va oxirida ko'rsatiladi.
        try:
            documents = load_file(path, data_dir)
        except Exception as error:  # Exception — deyarli barcha xatolarning umumiy turi; "as error" — xato obyektini olamiz
            # type(error).__name__ — xato turi nomi, masalan "FileDataError"
            result.failed_files[relative_path] = f"{type(error).__name__}: {error}"
            continue

        result.documents.extend(documents)  # .extend() — boshqa ro'yxatning BARCHA elementlarini qo'shadi (append — bittasini)
        result.loaded_files.append(relative_path)

    return result
