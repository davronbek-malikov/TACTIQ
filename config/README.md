# config: barcha sozlamalar bitta joyda

Ikkala pipeline va UI backend shu yerdan o'qiydi: `from config.settings import get_settings`.

## Fayllar

| Fayl | Nima qiladi |
|---|---|
| `settings.py` | `Settings` (default qiymatlar) + `get_settings()` (`.env` dan o'qiydi) |
| `__init__.py` | qisqa import: `from config import get_settings` |

## Qanday ishlaydi

```
.env (yoki environment variable)  ->  get_settings()  ->  Settings(...)
bo'sh / yo'q bo'lsa               ->  Settings'dagi default qiymat
```

| `.env` kaliti | `Settings` maydoni | Default |
|---|---|---|
| `TACTIQ_RAW_DATA_DIR` | `raw_data_dir` | `Indexing/01_documents/sample_docs` |
| `TACTIQ_CHUNK_SIZE` / `_OVERLAP` | `chunk_size` / `chunk_overlap` | 500 / 50 |
| `TACTIQ_EMBEDDING_MODEL` | `embedding_model_name` | `sentence-transformers/all-MiniLM-L6-v2` |
| `QDRANT_URL` | `qdrant_url` | `http://localhost:6333` |
| `QDRANT_COLLECTION` | `qdrant_collection` | `tactiq_documents` |
| `QDRANT_LOCAL_PATH` | `qdrant_local_path` | bo'sh → server rejimi |
| `TACTIQ_OFFLINE` | `is_offline()` | `0` → internetli; `1` → internetsiz (faqat qwen, HF keshdan, Qdrant Cloud taqiqlangan) |

LLM kalitlari (`GROQ_API_KEY`, `GEMINI_API_KEY`) `Settings`'da emas: ularni
`Retrieval_Generation/06_llm_generation` to'g'ridan-to'g'ri `os.getenv()` bilan o'qiydi.

## Kutubxonalar

```python
from dotenv import load_dotenv     # .env faylini environment'ga yuklaydi (pip install python-dotenv)
import os                          # os.getenv("QDRANT_URL"): qiymatni o'qish
from dataclasses import dataclass  # @dataclass(frozen=True): o'zgarmas sozlamalar
from pathlib import Path           # nisbiy yo'l -> loyiha ildiziga nisbatan
```

`.env` git'ga tushmaydi (kalitlar uchun). Namuna: [`.env.example`](../.env.example).
