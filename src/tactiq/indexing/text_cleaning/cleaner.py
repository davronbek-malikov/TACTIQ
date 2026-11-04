"""
Text Cleaning — 2-bosqich

PDF va DOCX'dan olingan matn ko'pincha "iflos" bo'ladi: ortiqcha bo'sh joylar,
ketma-ket bo'sh qatorlar, ko'rinmas control belgilar. Bular:
  * token'larni behuda sarflaydi (chunk'ga kamroq foydali matn sig'adi);
  * embedding sifatini biroz buzadi.

Bu modul matnni EHTIYOTKORLIK bilan tozalaydi:
  * tinish belgilari, raqamlar va katta-kichik harflar o'zgarmaydi;
  * "4-3-3", "xG", "Gündoğan" kabi futbol atamalari va ismlar o'zgarmaydi.
Agressiv tozalash (masalan, barcha belgilarni o'chirish) matn ma'nosini buzishi mumkin.

Input:  Document (Document Loading'dan)
Output: matni tozalangan yangi Document (metadata o'zgarmaydi)

Keyingi bosqich: Metadata.
"""

import re
import unicodedata
from dataclasses import dataclass

from tactiq.indexing.document_loading import Document

# Regular expression (regex) — matndagi naqshlarni (pattern) qidirish tili.
# re.compile() naqshni bir marta tayyorlaydi, keyin uni ko'p marta tez ishlatamiz.

# Control belgilar: ko'rinmaydigan maxsus belgilar (\x00 ... \x1f, \x7f).
# \n (yangi qator) va \t (tab) bundan mustasno — ular matn tuzilishi uchun kerak.
CONTROL_CHARACTERS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
# Bitta yoki undan ko'p bo'sh joy / tab
REPEATED_SPACES = re.compile(r"[ \t]+")
# Uch va undan ko'p ketma-ket yangi qator -> bitta bo'sh qator (paragraph chegarasi saqlanadi)
REPEATED_NEWLINES = re.compile(r"\n{3,}")


@dataclass(frozen=True)
class CleaningConfig:
    """Qaysi tozalash qadamlari yoqilganini belgilaydi (har birini alohida o'chirish mumkin).

    frozen=True — obyektni yaratilgandan keyin o'zgartirib bo'lmaydi. Shu sababli
    `config: CleaningConfig = CleaningConfig()` default qiymati xavfsiz: uni hech kim
    tasodifan o'zgartirib, boshqa chaqiruvlarga ta'sir qila olmaydi.
    Misol: CleaningConfig(collapse_newlines=False) — qatorlarni birlashtirmaslik.
    """

    normalize_unicode: bool = True
    remove_control_characters: bool = True
    collapse_spaces: bool = True
    collapse_newlines: bool = True


def clean_text(text: str, config: CleaningConfig = CleaningConfig()) -> str:
    """Bitta matnni tozalaydi.

    Input:  text — xom (raw) matn; config — qaysi qadamlar bajarilishi.
    Output: tozalangan matn. Agar matn faqat bo'sh joylardan iborat bo'lsa — "" (bo'sh string).
    """
    if not text:
        return ""

    # Windows (\r\n) va eski Mac (\r) qator tugashlarini bitta standart \n ga keltiramiz.
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    if config.normalize_unicode:
        # NFC — bir xil ko'rinadigan harflarni bir xil kodga keltiradi.
        # Masalan "ü" ikki xil yozilishi mumkin: bitta belgi yoki "u" + nuqtalar.
        # NFC ikkalasini bitta belgiga birlashtiradi, harfni o'chirmaydi.
        text = unicodedata.normalize("NFC", text)
        # Non-breaking space ( ) PDF'larda ko'p uchraydi — oddiy bo'sh joyga almashtiramiz.
        text = text.replace(" ", " ")

    if config.remove_control_characters:
        text = CONTROL_CHARACTERS.sub("", text)

    if config.collapse_spaces:
        text = REPEATED_SPACES.sub(" ", text)
        # Har bir qatorning boshidagi va oxiridagi bo'sh joylarni olib tashlaymiz.
        lines = [line.strip() for line in text.split("\n")]
        text = "\n".join(lines)

    if config.collapse_newlines:
        text = REPEATED_NEWLINES.sub("\n\n", text)

    return text.strip()


def clean_document(document: Document, config: CleaningConfig = CleaningConfig()) -> Document:
    """Document matnini tozalaydi va YANGI Document qaytaradi.

    Asl Document o'zgartirilmaydi. metadata nusxalanadi (dict(...)), shuning uchun
    keyingi bosqichlar metadata'ni o'zgartirsa ham asl obyekt buzilmaydi.
    """
    return Document(
        text=clean_text(document.text, config),
        metadata=dict(document.metadata),
    )
