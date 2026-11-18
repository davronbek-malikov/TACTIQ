# 04: Top-k Retrieval

**Eng mos k ta chunk'ni tanlash.**

## Nazariya

```
03 natijasi:  0.71  0.58  0.44  0.21  0.12 ...
k = 3      ->  0.71  0.58  0.44
min_score = 0.3 -> past score'lar tashlanadi
```

- **k**: LLM'ga nechta chunk beramiz. Kichik k: kam kontekst; katta k: ortiqcha "shovqin" va qimmatroq prompt.
- **min_score**: undan past chunk savolga aloqador emas.
- Hech bir chunk qolmasa: LLM **chaqirilmaydi**. Javobni o'ylab topishdan (hallucination) himoya.

## Kod: [top_k_retrieval.py](top_k_retrieval.py)

| Nom | Nima |
|---|---|
| `RetrievedChunk` | `text`, `source`, `page`, `score`: keyingi bosqichlar shu bilan ishlaydi |
| `select_top_k(points, k=3, min_score=0.3)` | Qdrant point'lari → `list[RetrievedChunk]` |

## Kutubxonalar

```python
from dataclasses import dataclass   # RetrievedChunk: oddiy ma'lumot class'i
from typing import Optional         # page: Optional[int]: TXT/MD da sahifa yo'q (None)
```

## Amaliyot

```bash
python Retrieval_Generation/04_top_k_retrieval/top_k_retrieval.py
```
Ko'rinadi: har bir namunaviy savol uchun nechta chunk tanlandi. "World Cup" savolida: 0 ta.

**Keyingi:** [05, Prompt Construction](../05_prompt_construction/README.md)
