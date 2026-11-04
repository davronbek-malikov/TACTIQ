# __init__.py — bu papkani Python "package" (paket)ga aylantiradi: shunda uni import qilish mumkin.
# Bu yerda papka ichidagi asosiy nomlarni "yuqoriga chiqaramiz" (re-export). Natijada boshqa fayllar
# uzun yo'l o'rniga qisqa import yozadi, masalan:
#     from indexing.step2_metadata import attach_metadata
#     (from indexing.step2_metadata.metadata_builder import attach_metadata o'rniga)

from indexing.step2_metadata.metadata_builder import (
    OPTIONAL_FIELDS,
    TACTIQ_NAMESPACE,
    attach_metadata,
    build_metadata,
    make_document_id,
    read_sidecar_metadata,
)

# __all__ — bu paketning "rasmiy" (tashqariga ochiq) nomlari ro'yxati;
# "from ... import *" yozilganda aynan shu nomlar import qilinadi.
__all__ = [
    "OPTIONAL_FIELDS",
    "TACTIQ_NAMESPACE",
    "attach_metadata",
    "build_metadata",
    "make_document_id",
    "read_sidecar_metadata",
]
