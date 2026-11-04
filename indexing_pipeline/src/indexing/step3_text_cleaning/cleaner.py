"""
Text Cleaning — 3-bosqich

PDF va DOCX'dan olingan matn ko'pincha "iflos" bo'ladi: ortiqcha bo'sh joylar,
ketma-ket bo'sh qatorlar, ko'rinmas control belgilar. Bular:
  * token'larni behuda sarflaydi (chunk'ga kamroq foydali matn sig'adi);
  * embedding sifatini biroz buzadi.

Bu modul matnni EHTIYOTKORLIK bilan tozalaydi:
  * tinish belgilari, raqamlar va katta-kichik harflar o'zgarmaydi;
  * "4-3-3", "xG", "Gündoğan" kabi futbol atamalari va ismlar o'zgarmaydi.
Agressiv tozalash (masalan, barcha belgilarni o'chirish) matn ma'nosini buzishi mumkin.

Input:  metadata'ga ega Document (Metadata bosqichidan)
Output: matni tozalangan yangi Document (metadata o'zgarmaydi)

Keyingi bosqich: Chunking.
"""

import re  # re — regular expression (regex): matndan naqsh (pattern) bo'yicha qidirish va almashtirish kutubxonasi
import unicodedata  # unicodedata — Unicode harflar bilan ishlash (masalan, bir xil harfni bir xil kodga keltirish)
from dataclasses import dataclass  # dataclass — sozlamalar class'ini qisqa yozish uchun

from indexing.step1_document_loading import Document  # 1-bosqichdagi Document dataclass

# re.compile() naqshni bir marta tayyorlaydi, keyin uni ko'p marta tez ishlatamiz.
# r"..." — raw string: "\" belgisi Python tomonidan o'zgartirilmaydi, to'g'ridan-to'g'ri regex'ga boradi.

# Control belgilar: ko'rinmaydigan maxsus belgilar (\x00 ... \x1f, \x7f).
# [ ... ] — "shu belgilardan istalgan bittasi". \n (yangi qator) va \t (tab) bundan mustasno —
# ular matn tuzilishi uchun kerak, shuning uchun ro'yxatga kiritilmagan.
CONTROL_CHARACTERS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
# [ \t]+ — bitta yoki undan ko'p ("+") bo'sh joy yoki tab
REPEATED_SPACES = re.compile(r"[ \t]+")
# \n{3,} — uch va undan ko'p ketma-ket yangi qator -> bitta bo'sh qatorga qisqartiramiz (paragraph chegarasi saqlanadi)
REPEATED_NEWLINES = re.compile(r"\n{3,}")

# Non-breaking space — oddiy bo'sh joyga o'xshaydi, lekin boshqa belgi. PDF'larda ko'p uchraydi.
# "\u00a0" — uning Unicode kodi. Kodda ko'rinadigan bo'lishi uchun belgining o'zini emas, kodini yozamiz.
NON_BREAKING_SPACE = "\u00a0"


# frozen=True — obyektni yaratilgandan keyin o'zgartirib bo'lmaydi. Shu sababli
# `config: CleaningConfig = CleaningConfig()` default qiymati xavfsiz: uni hech kim
# tasodifan o'zgartirib, boshqa chaqiruvlarga ta'sir qila olmaydi.
@dataclass(frozen=True)
class CleaningConfig:
    """Qaysi tozalash qadamlari yoqilganini belgilaydi (har birini alohida o'chirish mumkin).

    Misol: CleaningConfig(collapse_newlines=False) — qatorlarni birlashtirmaslik.
    """

    normalize_unicode: bool = True          # bool — True (ha) yoki False (yo'q)
    remove_control_characters: bool = True
    collapse_spaces: bool = True
    collapse_newlines: bool = True


def clean_text(text: str, config: CleaningConfig = CleaningConfig()) -> str:
    """Bitta matnni tozalaydi.

    Input:  text — xom (raw) matn; config — qaysi qadamlar bajarilishi.
    Output: tozalangan matn. Agar matn faqat bo'sh joylardan iborat bo'lsa — "" (bo'sh string).
    """
    if not text:  # bo'sh string "" Python'da False hisoblanadi, shuning uchun "not text" — "matn bo'shmi?"
        return ""

    # Windows (\r\n) va eski Mac (\r) qator tugashlarini bitta standart \n ga keltiramiz.
    # .replace(a, b) — matndagi barcha a'larni b'ga almashtiradi.
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    if config.normalize_unicode:
        # NFC — bir xil ko'rinadigan harflarni bir xil kodga keltiradi.
        # Masalan "ü" ikki xil yozilishi mumkin: bitta belgi yoki "u" + nuqtalar.
        # NFC ikkalasini bitta belgiga birlashtiradi, harfni o'chirmaydi.
        text = unicodedata.normalize("NFC", text)
        text = text.replace(NON_BREAKING_SPACE, " ")  # non-breaking space -> oddiy bo'sh joy

    if config.remove_control_characters:
        text = CONTROL_CHARACTERS.sub("", text)  # .sub(yangi, matn) — naqshga mos joylarni "yangi" bilan almashtiradi

    if config.collapse_spaces:
        text = REPEATED_SPACES.sub(" ", text)  # "a    b" -> "a b"
        # Har bir qatorning boshidagi va oxiridagi bo'sh joylarni olib tashlaymiz.
        lines = [line.strip() for line in text.split("\n")]  # .split("\n") — matnni qatorlar ro'yxatiga bo'ladi
        text = "\n".join(lines)  # qatorlarni yana bitta matnga ulaymiz

    if config.collapse_newlines:
        text = REPEATED_NEWLINES.sub("\n\n", text)

    return text.strip()  # oxirida butun matnning boshi va oxiridagi bo'sh joylar/qatorlarni olib tashlaymiz


def clean_document(document: Document, config: CleaningConfig = CleaningConfig()) -> Document:
    """Document matnini tozalaydi va YANGI Document qaytaradi.

    Asl Document o'zgartirilmaydi. metadata nusxalanadi (dict(...)), shuning uchun
    keyingi bosqichlar metadata'ni o'zgartirsa ham asl obyekt buzilmaydi.
    """
    return Document(
        text=clean_text(document.text, config),
        metadata=dict(document.metadata),  # dict(x) — x'ning yangi nusxasi (copy)
    )
