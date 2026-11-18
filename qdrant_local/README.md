# qdrant_local: Qdrant'ning diskdagi papkasi (Docker'siz)

Indexing (05) shu yerga **yozadi**, Retrieval (03) shu yerdan **qidiradi**.
Bu papka: ma'lumot, kod emas. Uni git'ga qo'shmaymiz (faqat shu README).

## Qdrant'ni ikki xil ishga tushirish

| | Server (Docker) | Local (`qdrant_local`) |
|---|---|---|
| Ishga tushirish | `docker compose up -d qdrant` | hech narsa: faqat papka |
| `.env` | `QDRANT_LOCAL_PATH=` (bo'sh) | `QDRANT_LOCAL_PATH=qdrant_local` |
| Ma'lumot qayerda | Docker volume ichida | shu papkada |
| Dashboard | http://localhost:6333/dashboard | yo'q |
| Bir vaqtda nechta dastur | ko'p | **faqat bitta** |
| Qachon | katta ma'lumot, production | dars, Docker ishlamasa |

Kod ikkalasida **bir xil**. Farq faqat 3 qatorda
([qdrant_store.py](../Indexing/05_vector_database/src/vector_database/qdrant_store.py)):

```python
def create_qdrant_client(url, api_key=None, local_path=None):
    if local_path:
        return QdrantClient(path=local_path)       # local: diskdagi papka
    return QdrantClient(url=url, api_key=api_key)  # server: Docker yoki Cloud
```

## Ichida nima bor

```text
qdrant_local/
├── meta.json                                   # collection'lar ro'yxati va sozlamasi (size=384, Cosine)
├── .lock                                       # "papka band" belgisi: bitta dastur ishlatyapti
└── collection/
    └── tactiq_documents/
        └── storage.sqlite                      # point'lar: id + vector + payload (SQLite jadvali)
```

- `meta.json`: `VectorParams(size=384, distance=COSINE)` ning diskdagi ko'rinishi.
- `storage.sqlite`: bitta `points` jadvali: `id` (chunk_id) + `point` (vector va payload, binary).
- Local rejimda **Qdrant server yo'q**: `qdrant-client` kutubxonasining o'zi "mini-Qdrant" bo'lib ishlaydi.
  Hamma vector'larni xotiraga yuklaydi va `numpy` bilan birma-bir solishtiradi (HNSW yo'q): kichik ma'lumot uchun yetarli.

## Amaliyot

```bash
# 1. .env faylida:
QDRANT_LOCAL_PATH=qdrant_local

# 2. Indexing: papka yaratiladi va to'ldiriladi
python Indexing/indexing_pipeline.py

# 3. Nima saqlandi
python Indexing/05_vector_database/scripts/step2_inspect_collection.py

# 4. Retrieval: shu papkadan qidiradi
python Retrieval_Generation/03_similarity_search/similarity_search.py
```

SQLite ichini ko'rish (ixtiyoriy):

```bash
python -c "import sqlite3; db = sqlite3.connect('qdrant_local/collection/tactiq_documents/storage.sqlite'); print(db.execute('select count(*) from points').fetchone())"
```

## Ko'p uchraydigan xatolar

| Xato | Sabab | Yechim |
|---|---|---|
| `Storage folder ... is already accessed by another instance` | boshqa dastur (masalan UI backend) papkani ochib turibdi | o'sha dasturni to'xtating (Ctrl+C) |
| Retrieval 0 ta natija beradi | Docker'da index qilingan, endi local rejim (yoki aksincha) | shu rejimda Indexing'ni qayta ishga tushiring |
| `Collection ... 384-o'lchamli, model esa ...` | boshqa embedding model | boshqa `QDRANT_COLLECTION` nomi yoki papkani o'chiring |

Qaytadan boshlash: `qdrant_local/` papkasini o'chiring (README'dan tashqari) va Indexing'ni qayta ishga tushiring.

## Kutubxonalar

```python
from qdrant_client import QdrantClient   # QdrantClient(path=...): local rejim (pip install qdrant-client)
import sqlite3                           # Python'da bor: storage.sqlite'ni ochib ko'rish uchun
```
