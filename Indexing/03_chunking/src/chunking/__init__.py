# __init__.py — bu papkani Python "package" (paket)ga aylantiradi: shunda uni import qilish mumkin.
# Bu yerda papka ichidagi asosiy nomlarni "yuqoriga chiqaramiz" (re-export). Natijada boshqa fayllar
# uzun yo'l o'rniga qisqa import yozadi, masalan:
#     from chunking import TokenTextSplitter
#     (from chunking.text_splitter import TokenTextSplitter o'rniga)

from chunking.text_splitter import (
    Chunk,
    TokenTextSplitter,
    make_chunk_id,
    make_token_windows,
)

# __all__ — bu paketning "rasmiy" (tashqariga ochiq) nomlari ro'yxati;
# "from ... import *" yozilganda aynan shu nomlar import qilinadi.
__all__ = [
    "Chunk",
    "TokenTextSplitter",
    "make_chunk_id",
    "make_token_windows",
]
