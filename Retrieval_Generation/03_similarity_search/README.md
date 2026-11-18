# 03: Similarity Search

**Savol vector'ini bazadagi vector'lar bilan solishtirish.**

## Nazariya

```
savol vector'i  ──►  Qdrant: har bir chunk vector'i bilan cosine  ──►  score bo'yicha tartiblangan ro'yxat
```

- **Cosine similarity**: ikki vector qanchalik bir yo'nalishda: `1`: juda o'xshash, `0`: aloqasi yo'q.
- Vector'lar normalize qilingan (uzunligi = 1), shuning uchun cosine = dot product.
- **HNSW index** (server/Docker): Qdrant hamma chunk'ni birma-bir tekshirmaydi, "qo'shnilar grafi" orqali tez topadi.
  **Local rejimda** HNSW yo'q: hamma vector'lar `numpy` bilan birma-bir solishtiriladi (kichik ma'lumot uchun yetarli).
- **Metadata filter** (`query_filter`): "faqat `topic = low_block` hujjatlaridan qidir". UI shuni ishlatadi.
- Qdrant qayerda bo'lishidan qat'i nazar (Docker yoki [qdrant_local](../../qdrant_local/README.md)) kod bir xil.

## Kod: [similarity_search.py](similarity_search.py)

| Nom | Nima |
|---|---|
| `similarity_search(client, collection, query_vector, limit=10, query_filter=None)` | eng o'xshash 10 ta point (score + payload) |

## Kutubxonalar

```python
from qdrant_client import QdrantClient           # client.query_points(...): vector qidiruv (pip install qdrant-client)
from vector_database import create_qdrant_client  # Indexing/05: server yoki local ulanish
```

## Amaliyot

```bash
python Retrieval_Generation/03_similarity_search/similarity_search.py
```
Ko'rinadi: har bir chunk'ning score'i va manbasi (kattadan kichikka).

**Keyingi:** [04, Top-k Retrieval](../04_top_k_retrieval/README.md)
