"""
Document — butun Indexing pipeline bo'ylab yuradigan asosiy ma'lumot tuzilmasi.

Har bir loader (PDF, DOCX, TXT, Markdown) natijani bir xil ko'rinishda qaytaradi: Document.
Shu sababli keyingi bosqichlar (Metadata, Text Cleaning, Chunking) fayl formatini bilishi shart emas.
"""

from dataclasses import dataclass, field  # dataclasses — Python'ning o'z (standart) kutubxonasi, o'rnatish shart emas.
#                                           dataclass — ma'lumot saqlovchi class'ni qisqa yozish uchun decorator.
#                                           field     — atributga maxsus sozlama berish uchun (masalan default_factory).


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
# Qachon dataclass, qachon oddiy class?
#   * class faqat ma'lumot saqlasa (__init__ faqat self.x = x qilsa)  -> @dataclass  (Document, Chunk)
#   * __init__ ichida ish bajarilsa (model yuklash, ulanish ochish)  -> oddiy class (EmbeddingModel)
@dataclass
class Document:  # class — o'z atributlari (ma'lumot) va metodlari (amallari) bo'lgan yangi tur (type) yaratadi.
    """Fayldan o'qilgan bitta matn bo'lagi.

    PDF uchun: har bir sahifa — alohida Document (page raqami metadata'da saqlanadi).
    DOCX / TXT / Markdown uchun: butun fayl — bitta Document.

    Atributlar:
        text:     fayldan ajratib olingan matn.
        metadata: matn qayerdan kelgani haqidagi ma'lumot
                  (source, source_path, file_type, page, keyinroq document_id va boshqalar).
    """

    text: str  # ": str" — type hint: bu atribut matn (string) bo'lishi kerakligini bildiradi.

    # field(default_factory=dict) — har bir yangi Document uchun ALOHIDA bo'sh dict yaratadi.
    # Agar `metadata: dict = {}` deb yozsak, barcha obyektlar bitta umumiy dict'ni bo'lishib
    # qolardi — bu Python'dagi mashhur xato, dataclass uni ruxsat ham bermaydi.
    metadata: dict = field(default_factory=dict)  # dict — "kalit: qiymat" juftliklari, masalan {"page": 2}
