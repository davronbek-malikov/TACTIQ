# __init__.py — bu papkani Python "package" (paket)ga aylantiradi: shunda uni import qilish mumkin.
# Bu yerda papka ichidagi asosiy nomlarni "yuqoriga chiqaramiz" (re-export). Natijada boshqa fayllar
# uzun yo'l o'rniga qisqa import yozadi, masalan:
#     from indexing.step1_document_loading import load_directory
#     (from indexing.step1_document_loading.loader import load_directory o'rniga)

from indexing.step1_document_loading.document import Document
from indexing.step1_document_loading.loader import (
    SUPPORTED_EXTENSIONS,
    LoadResult,
    discover_files,
    load_directory,
    load_file,
)

# __all__ — bu paketning "rasmiy" (tashqariga ochiq) nomlari ro'yxati;
# "from ... import *" yozilganda aynan shu nomlar import qilinadi.
__all__ = [
    "SUPPORTED_EXTENSIONS",
    "Document",
    "LoadResult",
    "discover_files",
    "load_directory",
    "load_file",
]
