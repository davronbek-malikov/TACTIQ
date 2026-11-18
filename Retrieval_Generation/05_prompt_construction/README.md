# 05: Prompt Construction

**Savol + topilgan kontekstni LLM uchun bitta xabarga birlashtirish.**

## Nazariya

```
system: "Faqat kontekst asosida javob ber. Bilmasang: bilmayman de. Manbani [1] kabi ko'rsat."
user:   Context:
        [1] (counterpressing.pdf, page 1)  ...chunk matni...
        [2] (low_block.txt, page None)     ...chunk matni...
        Question: What is counterpressing?
```

- **System prompt**: LLM uchun qoidalar (rol, cheklovlar, format).
- **Context**: raqamlangan chunk'lar. Raqam `[1]` keyin javobda manba sifatida qaytadi.
- RAG'ning asosiy g'oyasi: LLM o'z xotirasidan emas, **bizning hujjatlardan** javob beradi.

## Kod: [prompt_construction.py](prompt_construction.py)

| Nom | Nima |
|---|---|
| `SYSTEM_PROMPT` | LLM qoidalari |
| `build_context(chunks)` | chunk'lar → `[1] (manba, sahifa)\nmatn` |
| `build_messages(question, chunks)` | `[{"role": "system", ...}, {"role": "user", ...}]` |

## Kutubxonalar

Yo'q: faqat Python string'lari (f-string, `"\n\n".join`).
`messages` formati: OpenAI Chat API standarti (06-bosqich shuni yuboradi).

## Amaliyot

```bash
python Retrieval_Generation/05_prompt_construction/prompt_construction.py
```
Ko'rinadi: LLM'ga **aynan** nima yuboriladi.

**Keyingi:** [06, LLM Generation](../06_llm_generation/README.md)
