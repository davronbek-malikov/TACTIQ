# UI backend: FastAPI

Brauzer va ikki pipeline o'rtasidagi **ko'prik**. Yangi RAG kodi yo'q: Indexing va Retrieval_Generation funksiyalari **import** qilinadi.

```
Brauzer  --HTTP JSON-->  main.py (endpoint)  -->  documents / indexing_jobs / investigate  -->  Indexing + RG kodi  -->  Qdrant
```

## Fayllar (o'qish tartibi)

| Fayl | Nima qiladi | Qaysi pipeline kodini chaqiradi |
|---|---|---|
| [core.py](core.py) | sozlamalar, bitta embedding model, bitta Qdrant ulanishi, `qdrant_lock` | `config`, `EmbeddingModel`, `create_qdrant_client` |
| [schemas.py](schemas.py) | so'rov/javob shakllari: `InvestigateRequest`, `Evidence`, `Step` ... |: |
| [main.py](main.py) | barcha `/api/...` endpoint'lar; Python xatosi → HTTP status | hammasi shu yerdan |
| [documents.py](documents.py) | hujjatlar ro'yxati, tafsilot, upload, metadata, o'chirish | `document_loading` (02) |
| [indexing_jobs.py](indexing_jobs.py) | Indexing'ni fonda (thread) ishga tushiradi, tarixni saqlaydi | `run_indexing_pipeline` (01–05) |
| [investigate.py](investigate.py) | savol → 7 bosqich, har birining vaqti; RAG / LLM only rejimi | Retrieval_Generation 01–07 |
| `tests/test_api.py` | API testlari (vaqtinchalik papka, local Qdrant, soxta LLM) |: |
| `runtime/` | `indexing_history.json` (git'ga tushmaydi) |: |

## Muhim g'oyalar

- **Bitta Qdrant ulanishi** (`core.get_qdrant_client`): [local rejimda](../../qdrant_local/README.md) papkani faqat bitta client ochishi mumkin.
- **`qdrant_lock`**: local rejimda so'rovlar navbat bilan; server rejimida qulf kerak emas.
- **Model bir marta yuklanadi**: birinchi savolda (~5 s), keyin tez.
- **Halol javob**: mos chunk yo'q bo'lsa LLM chaqirilmaydi; LLM ishlamasa aniq xato qaytadi.
- **API kalitlar hech qachon qaytarilmaydi**: `/api/llms` faqat "sozlangan / yo'q" deydi.

## Endpoint'lar

| Method | Endpoint | Fayl |
|---|---|---|
| GET | `/api/health`, `/api/system`, `/api/collections`, `/api/llms` | main.py |
| GET / POST / PUT / DELETE | `/api/documents...` | documents.py |
| POST / GET | `/api/indexing/jobs`, `/api/indexing/history` | indexing_jobs.py |
| POST | `/api/investigate` | investigate.py |

Hammasini brauzerda sinash: **http://localhost:8000/docs** (FastAPI avtomatik yaratadi).

## Kutubxonalar

```python
from fastapi import FastAPI, UploadFile, HTTPException  # web API: endpoint'lar, fayl yuklash (pip install fastapi)
from fastapi.middleware.cors import CORSMiddleware      # brauzer :3000 -> backend :8000 ruxsat
from pydantic import BaseModel, Field                   # JSON shaklini tekshirish (fastapi bilan keladi)
import uvicorn                                          # serverni ishga tushirish (pip install uvicorn)
# python-multipart                                      # UploadFile/Form uchun kerak (pip install python-multipart)
import threading, contextlib                            # fonda indexing, qulflar
import time, uuid, json                                 # bosqich vaqti, job id, tarix fayli
```

## Ishga tushirish

```bash
python UI/backend/main.py              # http://localhost:8000
python -m pytest UI/backend/tests      # testlar
```
