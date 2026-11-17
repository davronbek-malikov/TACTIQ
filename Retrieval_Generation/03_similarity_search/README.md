# 03: Similarity Search

**Savol vectorini bazadagi vectorlar bilan solishtirish.**

- Kod: [similarity_search.py](similarity_search.py): `similarity_search()` Qdrant'dan eng o'xshash point'larni **score** bilan oladi.
- **Score**: cosine similarity: 1 ga qancha yaqin bo'lsa, chunk savolga shuncha o'xshash.
- Qdrant buni HNSW index yordamida juda tez qiladi.

```bash
docker compose up -d qdrant
python Retrieval_Generation/03_similarity_search/similarity_search.py
```

**Keyingi:** [04, Top-k Retrieval](../04_top_k_retrieval/README.md)
