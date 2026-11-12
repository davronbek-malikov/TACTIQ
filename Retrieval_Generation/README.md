# Retrieval & Generation Pipeline

RAG'ning ikkinchi pipeline'i: **foydalanuvchi savol berganda** ishlaydi.
Indexing tayyorlagan Qdrant collection'idan mos chunk'larni topadi va LLM yordamida manbali javob yozadi.

```
01 User Question -> 02 Query Embedding -> 03 Similarity Search -> 04 Top-k Retrieval
                 -> 05 Prompt Construction -> 06 LLM Generation -> 07 Answer + Sources
```

## Papkalar

Har bir papkada: `README.md` (nazariya) + bitta kod fayli. Kod faylini to'g'ridan-to'g'ri ishga tushirsangiz, o'sha bosqich natijasini ko'rsatadi.

| Bosqich | Kod | Amaliyot |
|---|---|---|
| [01 User Question](01_user_question/README.md) | `user_question.py` | namunaviy savollar |
| [02 Query Embedding](02_query_embedding/README.md) | `query_embedding.py` | savol → 384 ta son |
| [03 Similarity Search](03_similarity_search/README.md) | `similarity_search.py` | har bir chunk'ning score'i |
| [04 Top-k Retrieval](04_top_k_retrieval/README.md) | `top_k_retrieval.py` | eng mos 3 ta chunk |
| [05 Prompt Construction](05_prompt_construction/README.md) | `prompt_construction.py` | LLM'ga yuboriladigan matn |
| [06 LLM Generation](06_llm_generation/README.md) | `llm_generation.py` | qwen / groq / gemini javobi |
| [07 Answer + Sources](07_answer_sources/README.md) | `answer_sources.py` | javob + manbalar |

Ishga tushirish (loyiha ildizidan):
```bash
python Retrieval_Generation/<papka>/<fayl>.py
python Retrieval_Generation/rag_pipeline.py --llm groq --question "What is a low block?"
```

## Tayyorgarlik

1. **Indexing bajarilgan bo'lishi kerak:** `python Indexing/indexing_pipeline.py` (Qdrant'da chunk'lar bo'lsin).
2. **LLM:** kamida bittasini sozlang (`.env.example` → `.env`):
   - **qwen:** [Ollama](https://ollama.com) o'rnating, so'ng `ollama pull qwen2.5:1.5b`
   - **groq:** `GROQ_API_KEY=` — kalit: https://console.groq.com/keys
   - **gemini:** `GEMINI_API_KEY=` — kalit: https://aistudio.google.com/apikey

## Indexing bilan bog'liqlik

- **02** — Indexing'dagi `EmbeddingModel` import qilinadi (bir xil model).
- **03** — Indexing to'ldirgan `tactiq_documents` collection'idan qidiriladi.
- **07** — payload'dagi `source` va `page` manba sifatida ko'rsatiladi.

## Testlar

```bash
python -m pytest Retrieval_Generation
```
