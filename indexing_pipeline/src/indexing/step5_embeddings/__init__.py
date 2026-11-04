# __init__.py — bu papkani Python "package" (paket)ga aylantiradi: shunda uni import qilish mumkin.
# Bu yerda papka ichidagi asosiy nomlarni "yuqoriga chiqaramiz" (re-export). Natijada boshqa fayllar
# uzun yo'l o'rniga qisqa import yozadi, masalan:
#     from indexing.step5_embeddings import EmbeddingModel
#     (from indexing.step5_embeddings.embedding_model import EmbeddingModel o'rniga)

from indexing.step5_embeddings.embedding_model import EmbeddingModel

# __all__ — bu paketning "rasmiy" (tashqariga ochiq) nomlari ro'yxati;
# "from ... import *" yozilganda aynan shu nomlar import qilinadi.
__all__ = [
    "EmbeddingModel",
]
