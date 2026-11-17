# 04: Top-k Retrieval

**Eng mos hujjat qismlarini tanlash.**

- Kod: [top_k_retrieval.py](top_k_retrieval.py): `select_top_k(points, k=3, min_score=0.3)`.
- **k**: nechta chunk olinadi (standart 3).
- **min_score**: undan past chunk'lar tashlanadi: ular savolga aloqador emas.
- Hech qanday chunk qolmasa, LLM **chaqirilmaydi**: javob o'ylab topilmaydi.

```bash
python Retrieval_Generation/04_top_k_retrieval/top_k_retrieval.py
```
Barcha namunaviy savollar uchun nechta chunk tanlanganini ko'rsatadi.

**Keyingi:** [05, Prompt Construction](../05_prompt_construction/README.md)
