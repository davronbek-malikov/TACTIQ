# __init__.py — bu papkani Python "package" (paket)ga aylantiradi: shunda uni import qilish mumkin.
# Bu yerda papka ichidagi asosiy nomlarni "yuqoriga chiqaramiz" (re-export). Natijada boshqa fayllar
# uzun yo'l o'rniga qisqa import yozadi, masalan:
#     from vector_database import QdrantStore
#     (from vector_database.qdrant_store import QdrantStore o'rniga)

from vector_database.qdrant_store import (
    QdrantStore,
    build_payload,
    create_qdrant_client,
)

# __all__ — bu paketning "rasmiy" (tashqariga ochiq) nomlari ro'yxati;
# "from ... import *" yozilganda aynan shu nomlar import qilinadi.
__all__ = [
    "QdrantStore",
    "build_payload",
    "create_qdrant_client",
]
