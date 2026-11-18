# 04: Embedding Model

**Har bir chunk uchun vector yaratish.** Kod: [embedder.py](src/embedding_model/embedder.py)

## Nazariya

**Embedding**: matn ma'nosini ifodalovchi sonlar ro'yxati (vector):
`"high press"` → `[0.021, -0.113, ..., 0.045]` (384 ta son).

- **Nima uchun vector?** Kompyuter ma'noni solishtira olmaydi, sonlarni esa oladi. Ma'nosi yaqin matnlarning vector'lari yaqin.
- **Vector dimension**: vector'dagi sonlar soni (`all-MiniLM-L6-v2` → **384**). Kodda qo'lda yozilmaydi, model natijasidan olinadi.
- **Cosine similarity**: ikki vector qanchalik bir yo'nalishda. Vector'lar normalize qilingani (uzunligi = 1) uchun u oddiy dot product'ga teng.
- **Bir xil model qoidasi**: hujjatlar va keyinchalik foydalanuvchi savollari **aynan bir xil** model bilan embed qilinishi shart.
- **Batch processing**: matnlar guruh-guruh (32 tadan) model'dan o'tkaziladi: tezroq va xotira to'lmaydi.
- **max_seq_length = 256**: undan uzun chunk'ning oxiri vector'ga kirmaydi. Pipeline buni ogohlantiradi.

Model: [`sentence-transformers/all-MiniLM-L6-v2`](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2) (Hugging Face, ~90 MB, birinchi ishga tushirishda yuklanadi).

## Fayllar

| Fayl | Nima qiladi |
|---|---|
| `src/embedding_model/embedder.py` | `EmbeddingModel`: modelni yuklash, `dimension`, `embed()`, `validate()` |
| `scripts/run_embedding.py` | vector shakli, norm va ma'no yaqinligini ko'rsatadi |
| `tests/test_embeddings.py` | shakl (n, 384), norm = 1, o'xshash matnlar yaqin |

## Kutubxonalar

```python
from sentence_transformers import SentenceTransformer  # embedding model (pip install sentence-transformers; torch bilan keladi)
import numpy as np                                     # vector'lar: shape, norm, vstack, dot product (@)
```

## Amaliyot

```bash
python Indexing/04_embedding_model/scripts/run_embedding.py
```

Ko'rinadi: dimension va max_seq_length → `vectors.shape = (7, 384)` → bitta vector'ning 8 ta soni →
norm = 1.0 → `"high press"` va `"aggressive pressing..."` yaqin (≈0.51), `"ticket prices"` uzoq (≈0.03).

## Testlar

```bash
pytest Indexing/04_embedding_model
```

**Keyingi bosqich:** [05, Vector Database](../05_vector_database/README.md)
