"""
Document — barcha fayl formatlari uchun bitta umumiy shakl: text + metadata.

step1_load.py PDF, DOCX, TXT, MD fayllarni o'qib, shu shaklga soladi.
Keyingi bosqichlar fayl formatini bilmaydi — faqat Document bilan ishlaydi.
"""

from dataclasses import dataclass, field
@dataclass
class Document:
    """Fayldan o'qilgan bitta matn bo'lagi (PDF'da — bitta sahifa, boshqalarda — butun fayl)."""

    text: str                                     # fayldan o'qilgan matn
    metadata: dict = field(default_factory=dict)  # manba ma'lumoti: source, page ... (har biriga alohida dict)
