# 06 — LLM Generation

**Model javob yaratadi.** Kod: [llm_generation.py](llm_generation.py)

Uchta LLM — **bitta** `openai` kutubxonasi orqali (hammasi OpenAI-compatible API, faqat manzil farq qiladi):

| `--llm` | Qayerda | Nima ko'rsatadi | Kerak |
|---|---|---|---|
| `qwen` | o'z kompyuteringiz (Ollama) | internetsiz ishlash, ma'lumot xavfsizligi | Ollama + `ollama pull qwen2.5:1.5b` |
| `groq` | cloud | juda tez javob | `.env` da `GROQ_API_KEY` |
| `gemini` | cloud | bepul (free tier) | `.env` da `GEMINI_API_KEY` |

`temperature=0` — har safar bir xil, eng ishonchli javob.

```bash
python Retrieval_Generation/06_llm_generation/llm_generation.py --llm groq
```

**Keyingi:** [07 — Answer + Sources](../07_answer_sources/README.md)
