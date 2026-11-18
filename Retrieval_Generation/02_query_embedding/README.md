# 02: Query Embedding

**Savolni vector'ga aylantirish** (384 ta son).

## Nazariya

```
"What is counterpressing?"  ->  EmbeddingModel  ->  [0.021, -0.113, ..., 0.045]   (384 ta son)
```

- Chunk'lar Indexing'da vector'ga aylangan. Endi **savolni ham** vector'ga aylantiramiz: shunda ularni solishtirish mumkin.
- **Bir xil model qoidasi:** savol va chunk'lar **aynan bir xil** model bilan embed qilinadi (`all-MiniLM-L6-v2`).
  Boshqa model = boshqa "koordinata tizimi" → solishtirish ma'nosiz.
- Shuning uchun model ko'chirilmaydi: `Indexing/04_embedding_model` dan **import** qilinadi.

## Kod: [query_embedding.py](query_embedding.py)

| Nom | Nima |
|---|---|
| `embed_question(question, model)` | savol → `list[float]` (384 ta son) |

## Kutubxonalar

```python
from embedding_model import EmbeddingModel   # Indexing/04 dagi class (ichida sentence-transformers)
import sys; from pathlib import Path         # rag_paths orqali import yo'llarini sozlash
```

## Amaliyot

```bash
python Retrieval_Generation/02_query_embedding/query_embedding.py
```
Ko'rinadi: savol va vector'ning birinchi 6 ta soni.

**Keyingi:** [03, Similarity Search](../03_similarity_search/README.md)
