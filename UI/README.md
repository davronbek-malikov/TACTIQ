# UI: TACTIQ ilovasi (frontend + backend)

Ikki pipeline'ni brauzerda ko'rsatadigan ilova:

```
Brauzer (Next.js, :3000)  ->  Backend (FastAPI, :8000)  ->  Indexing + Retrieval_Generation kodi  ->  Qdrant (:6333)
```

Brauzer Qdrant'ga to'g'ridan-to'g'ri ulanmaydi, hammasi backend orqali. Backend yangi pipeline yozmaydi:
`Indexing/indexing_pipeline.py` va `Retrieval_Generation` bosqich funksiyalarini **import qiladi**.

## Tuzilma

```text
UI/
├── backend/                 # FastAPI (Python)
│   ├── main.py              # API endpoint'lar (ishga tushirish fayli)
│   ├── core.py              # umumiy resurslar: sozlamalar, embedding model, bitta Qdrant ulanishi
│   ├── schemas.py           # API kontraktlari (Pydantic)
│   ├── documents.py         # hujjatlar: ro'yxat, tafsilot, yuklash, metadata
│   ├── indexing_jobs.py     # Indexing pipeline'ni fonda ishga tushirish
│   ├── investigate.py       # Retrieval & Generation'ning 7 bosqichi (vaqti bilan)
│   └── tests/test_api.py
└── frontend/                # Next.js + TypeScript + Tailwind
    └── src/
        ├── app/             # 7 sahifa: Overview, Investigate, Knowledge, Matches, Players, Reports, Settings
        ├── components/      # ui/, layout/, investigate/, knowledge/, evidence/, video/
        └── lib/             # api.ts (backend bilan aloqa), types.ts (kontraktlar)
```

## Ishga tushirish (3 ta terminal, loyiha ildizidan)

**1. Qdrant**: ikki variantdan biri:

```Shell
docker compose up -d qdrant
```

Docker ishlamasa: `.env` faylida `QDRANT_LOCAL_PATH=qdrant_local`: Qdrant diskdagi papkada ishlaydi (Docker kerak emas).

**2. Backend** (`.venv` yoqilgan bo'lsin):

```powershell
pip install -r requirements.txt
python UI/backend/main.py          # http://localhost:8000  ·  API hujjatlari: http://localhost:8000/docs
```

**3. Frontend:**

```powershell
cd UI/frontend
npm install                        # faqat birinchi marta
npm run dev                        # http://localhost:3000
```

Brauzerda **http://localhost:3000** ni oching → **Knowledge** → *Sample documents → Index* → **Investigate**.

**LLM** (kamida bittasi, `.env` da): `GROQ_API_KEY`, `GEMINI_API_KEY` yoki Ollama (`ollama pull qwen2.5:1.5b`).
LLM sozlanmagan bo'lsa ham dalillar (evidence) topiladi, faqat javob o'rniga aniq xato ko'rsatiladi.

## Backend endpoint'lari

| Method | Endpoint                                    | Vazifasi                                                                  |
| ------ | ------------------------------------------- | ------------------------------------------------------------------------- |
| GET    | `/api/health`                             | backend ishlayaptimi                                                      |
| GET    | `/api/system`                             | Qdrant holati, collection, hujjatlar va chunk'lar soni, oxirgi indexing   |
| GET    | `/api/collections`                        | Qdrant collection'lari                                                    |
| GET    | `/api/llms`                               | Qwen / Groq / Gemini tayyormi (kalitlarning o'zi qaytarilmaydi)           |
| GET    | `/api/documents`                          | hujjatlar ro'yxati (metadata, chunk soni)                                 |
| GET    | `/api/documents/{source}/{file}`          | tafsilot: metadata, matn namunasi, chunk'lar                              |
| POST   | `/api/documents/upload`                   | faylni `my_documents` ga yuklash (format, nom, hajm tekshiriladi)       |
| PUT    | `/api/documents/{source}/{file}/metadata` | sidecar metadata (faqat `my_documents`)                                 |
| DELETE | `/api/documents/{source}/{file}`          | fayl + uning Qdrant chunk'larini o'chirish (faqat `my_documents`)       |
| POST   | `/api/indexing/jobs`                      | Indexing pipeline'ni ishga tushirish (`sample_docs` / `my_documents`) |
| GET    | `/api/indexing/jobs/{id}`                 | indexing holati va natijasi                                               |
| GET    | `/api/indexing/history`                   | indexing tarixi                                                           |
| POST   | `/api/investigate`                        | savol → 7 bosqich → javob + dalillar + bosqichlar vaqti                 |

## Nima ishlaydi va nima rejada

| Ishlaydi (haqiqiy ma'lumot)                                                                      | Rejada (halol "Coming soon")                                                    |
| ------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------- |
| Overview: Qdrant holati, hujjatlar/chunk'lar soni, indexing tarixi                               | Matches: tuzilgan o'yin ma'lumotlari (PostgreSQL)                               |
| Knowledge: yuklash, indexing, jadval, tafsilot, metadata tahriri, o'chirish                      | Players: o'yinchi profillari va statistika                                      |
| Investigate: 3 ta LLM, manbalar/filterlar, javob + bosiladigan `[1]` manbalar, 7 bosqich vaqti | Video workspace (V2): player, timeline, klip, kuzatuvlar, komponentlar tayyor |
| Reports: tekshiruvni saqlash (brauzerda) va Markdown eksport                                     | PDF eksport, rasm/ovoz/video kirish                                             |

Hech qayerda soxta javob, soxta son yoki soxta "ulandi" holati ko'rsatilmaydi.

## Testlar

```powershell
python -m pytest UI/backend/tests        # backend API (vaqtinchalik papka + local Qdrant, Docker kerak emas)
cd UI/frontend; npm run lint; npm run build
```
