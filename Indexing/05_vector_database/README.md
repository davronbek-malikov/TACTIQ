# 05 — Vector Database

**Vektorlar, matn va metadata'ni saqlash.** Kod: [qdrant_store.py](src/vector_database/qdrant_store.py)

## Nazariya

**Qdrant** — vector database. U **point**'larni saqlaydi:

| Qism | Misol | Nima uchun |
|---|---|---|
| `id` | `01d88625-...` (chunk_id) | Barqaror UUID — qayta yozilganda dublikat bo'lmaydi |
| `vector` | 384 ta son | Ma'no bo'yicha qidiruv (keyingi pipeline'da) |
| `payload` | `{"chunk_text": ..., "source": ..., "page": 2, "topic": ...}` | Natijani tushunish, citation, metadata filtering |

- **Collection** — SQL'dagi jadvalga o'xshash: bir xil o'lchamdagi vector'lar to'plami (`size=384`, `distance=COSINE`).
- **Nima uchun SQL yetmaydi?** SQL aniq qiymat bo'yicha qidiradi; bizga esa "ma'nosi yaqin" vector'lar kerak (HNSW index bilan tez).
- **upsert** = update + insert: shu ID bo'lsa yangilaydi, bo'lmasa qo'shadi. Pipeline'ni 10 marta ishga tushirsangiz ham nusxalar ko'paymaydi.
- **Payload index** — `topic`, `source` kabi maydonlar bo'yicha filter'ni tezlashtiradi.

## Amaliyot

```bash
docker compose up -d qdrant                                          # avval Qdrant
python Indexing/05_vector_database/scripts/step1_run_vector_database.py    # 02 -> 05 butun pipeline + bitta point
python Indexing/05_vector_database/scripts/step2_inspect_collection.py     # collection'da nima bor
```

Brauzerda: <http://localhost:6333/dashboard> → `tactiq_documents` collection.

`step1_run_vector_database.py` ni **ikki marta** ishga tushiring — "jami point'lar" soni o'zgarmasligi kerak.

## Testlar

```bash
pytest Indexing/05_vector_database     # 2 ta test Qdrant server'ni talab qiladi (bo'lmasa skip)
```

**Indexing tugadi.** Keyingi pipeline: Retrieval & Generation — savolni shu model bilan embed qilib,
Qdrant'dan eng yaqin chunk'larni topish.
