# __init__.py — bu papkani Python "package" (paket)ga aylantiradi: shunda uni import qilish mumkin.
# Bu yerda papka ichidagi asosiy nomlarni "yuqoriga chiqaramiz" (re-export). Natijada boshqa fayllar
# uzun yo'l o'rniga qisqa import yozadi, masalan:
#     from indexing.step3_text_cleaning import clean_document
#     (from indexing.step3_text_cleaning.cleaner import clean_document o'rniga)

from indexing.step3_text_cleaning.cleaner import CleaningConfig, clean_document, clean_text

# __all__ — bu paketning "rasmiy" (tashqariga ochiq) nomlari ro'yxati;
# "from ... import *" yozilganda aynan shu nomlar import qilinadi.
__all__ = [
    "CleaningConfig",
    "clean_document",
    "clean_text",
]
