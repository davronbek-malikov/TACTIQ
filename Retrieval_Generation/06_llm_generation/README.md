# 06: LLM Generation

**LLM kontekst asosida javob yozadi.**

## Nazariya

- **LLM** (Large Language Model): matnni davom ettiradigan model. U `messages` ni o'qib, javob yozadi.
- **OpenAI-compatible API**: ko'p provayderlar bir xil formatni qo'llaydi. Shuning uchun 3 ta LLM uchun
  **bitta** `openai` kutubxonasi yetadi, faqat `base_url` va kalit farq qiladi.
- **temperature = 0**: har safar bir xil, eng ishonchli javob (ijodkorlik kerak emas).

| `--llm` | Qayerda | Afzalligi | Kerak |
|---|---|---|---|
| `qwen` | o'z kompyuteringiz (Ollama) | internetsiz, ma'lumot tashqariga chiqmaydi | [Ollama](https://ollama.com) + `ollama pull qwen2.5:1.5b` |
| `groq` | cloud | juda tez | `.env` da `GROQ_API_KEY` |
| `gemini` | cloud | bepul (free tier) | `.env` da `GEMINI_API_KEY` |

## Internetli va internetsiz rejim

`.env` dagi **bitta kalit**:

| `TACTIQ_OFFLINE` | Rejim | LLM | Embedding | Qdrant |
|---|---|---|---|---|
| `0` | **online**: internetli | qwen, groq, gemini | Hugging Face'ni tekshiradi | local, Docker yoki Cloud |
| `1` | **offline**: on-premise | **faqat qwen** (groq/gemini → xato) | faqat keshdan | faqat local yoki Docker |

```bash
python check_mode.py        # tanlangan rejim uchun hammasi tayyormi
```

Offline rejimda ma'lumot (savol, chunk'lar, javob) kompyuterdan **chiqmaydi**.
Tekshirish: Wi-Fi'ni o'chiring → `--llm qwen` bilan savol bering.

Qayerda: [config/settings.py](../../config/settings.py) `is_offline()` · `generate_answer()` cloud LLM'ni bloklaydi · `UI/backend/main.py` `/api/llms`.

## Kod: [llm_generation.py](llm_generation.py)

| Nom | Nima |
|---|---|
| `LLM_PROVIDERS` | har bir LLM: `base_url`, kalit nomi, model nomi |
| `get_model_name(llm)` | `.env` dagi model (masalan `GROQ_MODEL`) yoki default |
| `generate_answer(messages, llm)` | xabarlarni LLM'ga yuboradi → javob matni |

## Kutubxonalar

```python
from openai import OpenAI   # OpenAI(base_url=..., api_key=...).chat.completions.create(...) (pip install openai)
import os                   # os.getenv("GROQ_API_KEY"): kalitni .env dan o'qish
import config.settings      # import qilinganda .env yuklanadi (python-dotenv)
```

## Amaliyot

```bash
python Retrieval_Generation/06_llm_generation/llm_generation.py --llm gemini
```
Ko'rinadi: LLM bitta oddiy savolga javob beradi (hali RAG'siz: kontekst yo'q).

**Keyingi:** [07, Answer + Sources](../07_answer_sources/README.md)
