# 05 — Prompt Construction

**Savol + topilgan kontekstni birlashtirish.**

- Kod: [prompt_construction.py](prompt_construction.py) — `build_messages()`.
- **System prompt** — LLM uchun qoidalar: faqat kontekst asosida javob ber, bo'lmasa "bilmayman" de, manbani `[1]` kabi ko'rsat.
- **User xabari** — raqamlangan chunk'lar (`[1] (manba, sahifa) matn`) + savol.

```bash
python Retrieval_Generation/05_prompt_construction/prompt_construction.py
```
LLM'ga aynan nima yuborilishini ko'rsatadi.

**Keyingi:** [06 — LLM Generation](../06_llm_generation/README.md)
