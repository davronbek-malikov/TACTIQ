# 07: Answer + Sources

**Javob va manbalarni foydalanuvchiga qaytarish.**

## Nazariya

```
Javob:     Counterpressing is pressing immediately after losing the ball [1] ...
Manbalar:  [1] counterpressing.pdf, page 1 (score 0.71)
           [2] defensive_transitions.md (score 0.55)
```

- **Manba (citation)**: RAG'ning oddiy LLM'dan asosiy afzalligi: javobni **tekshirish** mumkin.
- Javobdagi `[1]` → 05-bosqichdagi `[1]` chunk → Qdrant payload'idagi `source` va `page`.
- Mos chunk bo'lmasa: "Hujjatlarda bu savolga javob topilmadi.": LLM chaqirilmagan.

## Kod: [answer_sources.py](answer_sources.py)

| Nom | Nima |
|---|---|
| `RagAnswer` | `question`, `answer`, `llm`, `sources`: pipeline natijasi |
| `format_sources(chunks)` | `[1] fayl, page N (score 0.71)` qatorlari |
| `print_answer(result)` | javob + manbalarni ekranga chiqaradi |

Butun pipeline: [rag_pipeline.py](../rag_pipeline.py): `RagPipeline.ask()` 01 → 07 ni ketma-ket chaqiradi.

## Kutubxonalar

```python
from dataclasses import dataclass, field   # RagAnswer; field(default_factory=list): har biriga yangi ro'yxat
```

## Amaliyot

```bash
python Retrieval_Generation/07_answer_sources/answer_sources.py --llm gemini
python Retrieval_Generation/rag_pipeline.py --llm gemini --question "Who won the 2022 World Cup?"
```
Oxirgi bosqich: butun pipeline (01 → 07) ishlaydi. Ikkinchi buyruq: hujjatda yo'q savol → LLM chaqirilmaydi.

**Retrieval & Generation tugadi**: RAG to'liq ishlaydi. Keyingi: [UI](../../UI/README.md).
