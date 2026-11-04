"""
Document — butun Indexing pipeline bo'ylab yuradigan asosiy ma'lumot tuzilmasi.

Har bir loader (PDF, DOCX, TXT, Markdown) natijani bir xil ko'rinishda qaytaradi: Document.
Shu sababli keyingi bosqichlar (Text Cleaning, Metadata, Chunking) fayl formatini bilishi shart emas.
"""

from dataclasses import dataclass, field


# @dataclass — Python bizning o'rnimizga __init__() metodini yozib beradi.
# Ya'ni quyidagi class uchun Python avtomatik ravishda shunday constructor yaratadi:
#
#     def __init__(self, text: str, metadata: dict = <yangi bo'sh dict>):
#         self.text = text
#         self.metadata = metadata
#
# __init__ — obyekt yaratilayotganda (Document(...) chaqirilganda) ishlaydigan metod.
# self     — yaratilayotgan aniq obyektning o'zi. self.text — "shu obyektning text atributi".
#
# field(default_factory=dict) — har bir yangi Document uchun ALOHIDA bo'sh dict yaratadi.
# Agar `metadata: dict = {}` deb yozsak, barcha obyektlar bitta umumiy dict'ni bo'lishib
# qolardi — bu Python'dagi mashhur xato, dataclass uni ruxsat ham bermaydi.
@dataclass
class Document:
    """Fayldan o'qilgan bitta matn bo'lagi.

    PDF uchun: har bir sahifa — alohida Document (page raqami metadata'da saqlanadi).
    DOCX / TXT / Markdown uchun: butun fayl — bitta Document.

    Atributlar:
        text:     fayldan ajratib olingan matn.
        metadata: matn qayerdan kelgani haqidagi ma'lumot
                  (source, source_path, file_type, page, keyinroq document_id va boshqalar).
    """

    text: str
    metadata: dict = field(default_factory=dict)
