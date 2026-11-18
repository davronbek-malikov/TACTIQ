# 01: User Question

**Foydalanuvchi savoli**: pipeline'ning kirishi (input).

## Nazariya

- Indexing **oldin** bir marta ishlaydi. Retrieval & Generation esa **har bir savolda** ishlaydi.
- Savol: oddiy matn. Uni tozalaymiz (`strip`), bo'sh savolni rad etamiz.
- Savol turlari: hujjatda **bor** (javob topiladi) va hujjatda **yo'q** (tizim "bilmayman" deyishi kerak).

## Kod: [user_question.py](user_question.py)

| Nom | Nima |
|---|---|
| `SAMPLE_QUESTIONS` | 5 ta namunaviy savol. Oxirgisi (*Who won the 2022 World Cup?*) ataylab hujjatlarda yo'q |
| `prepare_question(question)` | bo'sh joylarni olib tashlaydi; bo'sh savol → `ValueError` |

## Kutubxonalar

Yo'q: faqat oddiy Python (`str.strip()`).

## Amaliyot

```bash
python Retrieval_Generation/01_user_question/user_question.py
```

**Keyingi:** [02, Query Embedding](../02_query_embedding/README.md)
