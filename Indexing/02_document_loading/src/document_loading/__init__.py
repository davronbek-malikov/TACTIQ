# __init__.py — bu papkani Python "package" (paket)ga aylantiradi: shunda uni import qilish mumkin.
# Bu yerda papka ichidagi asosiy nomlarni "yuqoriga chiqaramiz" (re-export). Natijada boshqa fayllar
# uzun yo'l o'rniga qisqa import yozadi, masalan:
#     from document_loading import load_directory
#     (from document_loading.loader import load_directory o'rniga)
#
# 02 — Document Loading paketi uch qismdan iborat (ishlash tartibida):
#     loader.py           -> 2.1  fayllarni topish va matnni o'qish
#     metadata_builder.py -> 2.2  document_id, source, page, topic ... biriktirish
#     cleaner.py          -> 2.3  matnni ehtiyotkorlik bilan tozalash
#     document.py         -> uchala qism uzatadigan Document dataclass

from document_loading.document import Document
from document_loading.loader import (
    SUPPORTED_EXTENSIONS,
    LoadResult,
    discover_files,
    load_directory,
    load_file,
)
from document_loading.metadata_builder import (
    OPTIONAL_FIELDS,
    TACTIQ_NAMESPACE,
    attach_metadata,
    build_metadata,
    make_document_id,
    read_sidecar_metadata,
)
from document_loading.cleaner import CleaningConfig, clean_document, clean_text

# __all__ — bu paketning "rasmiy" (tashqariga ochiq) nomlari ro'yxati;
# "from ... import *" yozilganda aynan shu nomlar import qilinadi.
__all__ = [
    "Document",
    # 2.1 loader
    "SUPPORTED_EXTENSIONS",
    "LoadResult",
    "discover_files",
    "load_directory",
    "load_file",
    # 2.2 metadata
    "OPTIONAL_FIELDS",
    "TACTIQ_NAMESPACE",
    "attach_metadata",
    "build_metadata",
    "make_document_id",
    "read_sidecar_metadata",
    # 2.3 cleaning
    "CleaningConfig",
    "clean_document",
    "clean_text",
]
