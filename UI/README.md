# UI: TACTIQ ilovasi (frontend + backend)

Ikki pipeline'ni brauzerda ko'rsatadigan ilova:

```
Brauzer (Next.js, :3000)  ->  Backend (FastAPI, :8000)  ->  Indexing + Retrieval_Generation kodi  ->  Qdrant (:6333)
```

Brauzer Qdrant'ga to'g'ridan-to'g'ri ulanmaydi, hammasi backend orqali. Backend yangi pipeline yozmaydi:
`Indexing/indexing_pipeline.py` va `Retrieval_Generation` bosqich funksiyalarini **import qiladi**.

## Tuzilma (har bir papkada README bor)

```text
UI/
├── backend/                 # FastAPI (Python)          -> backend/README.md
│   ├── main.py              # API endpoint'lar (ishga tushirish fayli)
│   ├── core.py              # umumiy resurslar: sozlamalar, embedding model, bitta Qdrant ulanishi
│   ├── schemas.py           # API kontraktlari (Pydantic)
│   ├── documents.py         # hujjatlar: ro'yxat, tafsilot, yuklash, metadata
│   ├── indexing_jobs.py     # Indexing pipeline'ni fonda ishga tushirish
│   ├── investigate.py       # Retrieval & Generation'ning 7 bosqichi (vaqti bilan)
│   └── tests/test_api.py
└── frontend/                # Next.js + TypeScript + Tailwind   -> frontend/README.md
    └── src/
        ├── app/             # 7 sahifa                   -> src/app/README.md
        ├── components/      # ui/, layout/, investigate/ -> src/components/README.md
        └── lib/             # api.ts, types.ts           -> src/lib/README.md
```

O'qish tartibi: [backend](backend/README.md) → [frontend](frontend/README.md) → [src/app](frontend/src/app/README.md) → [src/components](frontend/src/components/README.md) → [src/lib](frontend/src/lib/README.md).

## Bitta savolning yo'li (to'liq RAG)

```
1. Brauzer: Investigate sahifasida savol yoziladi           frontend/src/app/investigate/page.tsx
2. api.investigate() -> POST /api/investigate                frontend/src/lib/api.ts
3. FastAPI endpoint                                          backend/main.py
4. 7 bosqich, har birining vaqti                             backend/investigate.py
   01 prepare_question -> 02 embed_question -> 03 similarity_search -> 04 select_top_k
   -> 05 build_messages -> 06 generate_answer -> 07 javob + evidence   (Retrieval_Generation/)
5. JSON javob -> TurnView (javob, [1]) + EvidencePanel (chunk'lar)
```

## Ishga tushirish (3 ta terminal, loyiha ildizidan)

**1. Qdrant**: ikki variantdan biri:

```Shell
docker compose up -d qdrant
```

Docker ishlamasa: `.env` faylida `QDRANT_LOCAL_PATH=qdrant_local`: Qdrant diskdagi papkada ishlaydi (Docker kerak emas).
Diqqat: local rejimda backend ishlab turganda `python Indexing/...` skriptlari papkani ocha olmaydi:
indexing'ni UI'dagi **Knowledge → Index** tugmasi bilan qiling ([qdrant_local](../qdrant_local/README.md)).

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

## Internetli / internetsiz rejim

| | Online (`TACTIQ_OFFLINE=0`) | Offline (`TACTIQ_OFFLINE=1`) |
|---|---|---|
| LLM | Qwen, Groq, Gemini | faqat **Qwen** (Ollama) |
| UI tepa panel | `Online` belgisi | `Offline` belgisi |
| Settings sahifasi | *Online · cloud LLMs allowed* | *Offline · on-premise (Qwen only)* |

Almashtirish: `.env` da qiymatni o'zgartiring → backend'ni qayta ishga tushiring (Ctrl+C, `python UI/backend/main.py`).
Tayyorlikni tekshirish: `python check_mode.py` (loyiha ildizidan; Qdrant'ni ochmaydi, shuning uchun backend ishlab turganda ham ishlaydi).

Offline uchun bir martalik tayyorgarlik (internet bilan): [Ollama](https://ollama.com) o'rnatish → `ollama pull qwen2.5:1.5b`.

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
