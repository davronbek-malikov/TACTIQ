"""
2.3 Text Cleaning — ortiqcha bo'sh joy, bo'sh qator va ko'rinmas belgilarni olib tashlaydi.

Ehtiyotkor tozalash: harflar, raqamlar, tinish belgilari va "4-3-3", "xG" o'zgarmaydi.
Metadata o'zgarmaydi.

Keyingi bosqich: 03 — Chunking
"""

import re
import unicodedata
from dataclasses import dataclass

from document_loading.step0_document import Document

CONTROL_CHARACTERS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")  # ko'rinmas belgilar (\n va \t dan tashqari)
REPEATED_SPACES = re.compile(r"[ \t]+")                               # bir nechta bo'sh joy / tab
REPEATED_NEWLINES = re.compile(r"\n{3,}")                             # 3+ ketma-ket yangi qator
NON_BREAKING_SPACE = "\u00a0"                                         # PDF'dagi "maxsus" bo'sh joy


@dataclass(frozen=True)  # frozen — yaratilgandan keyin o'zgartirib bo'lmaydi
class CleaningConfig:
    """Qaysi tozalash qadamlari ishlashini belgilaydi."""

    normalize_unicode: bool = True
    remove_control_characters: bool = True
    collapse_spaces: bool = True
    collapse_newlines: bool = True


def clean_text(text: str, config: CleaningConfig = CleaningConfig()) -> str:
    """Bitta matnni tozalaydi. Faqat bo'sh joydan iborat matn -> ""."""
    if not text:
        return ""

    text = text.replace("\r\n", "\n").replace("\r", "\n")  # qator tugashlarini bir xil qilish

    if config.normalize_unicode:
        text = unicodedata.normalize("NFC", text)  # bir xil ko'rinadigan harflar -> bir xil kod
        text = text.replace(NON_BREAKING_SPACE, " ")

    if config.remove_control_characters:
        text = CONTROL_CHARACTERS.sub("", text)

    if config.collapse_spaces:
        text = REPEATED_SPACES.sub(" ", text)                 # "a    b" -> "a b"
        lines = [line.strip() for line in text.split("\n")]   # qator boshi/oxiridagi bo'sh joylar
        text = "\n".join(lines)

    if config.collapse_newlines:
        text = REPEATED_NEWLINES.sub("\n\n", text)            # ko'p bo'sh qator -> bitta bo'sh qator

    return text.strip()


def clean_document(document: Document, config: CleaningConfig = CleaningConfig()) -> Document:
    """Matni tozalangan YANGI Document qaytaradi (metadata nusxalanadi)."""
    return Document(
        text=clean_text(document.text, config),
        metadata=dict(document.metadata),
    )
