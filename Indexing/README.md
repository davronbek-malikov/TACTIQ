# Indexing Pipeline (Data Ingestion)

RAG'da ikkita pipeline bor:

1. **Indexing**: foydalanuvchi savol berishidan **oldin** ishlaydi: hujjatlarni vector'larga aylantirib, Vector Database'ga saqlaydi. ← **shu papka**
2. **Retrieval & Generation**: foydalanuvchi savol berganda ishlaydi → [Retrieval_Generation/](../Retrieval_Generation/README.md).

```
01 Documents  ->  02 Document Loading  ->  03 Chunking  ->  04 Embedding Model  ->  05 Vector Database
PDF, TXT,         fayllardan matnni         matnni kichik      har bir chunk uchun      vector'lar, matn va
DOCX ...          o'qish                    qismlarga bo'lish  vector yaratish          metadata'ni saqlash
```

## Papka tuzilishi

Har bir bosqich, alohida papka. Har birida: `README.md` (nazariya), `src/` (kod), `scripts/` (amaliyot), `tests/` (testlar).

```text
Indexing/
├── README.md                     # shu fayl
├── indexing_pipeline.py          # 02 -> 05 hammasini bitta buyruq bilan ishga tushiradi
├── indexing_pipeline.ipynb       # hamma bosqichlar bitta notebook'da, qadamma-qadam
├── indexing_paths.py             # import yo'llarini sozlaydi (har bir skript buni ishlatadi)
├── conftest.py                   # testlar uchun umumiy fixture'lar (model, tokenizer)
│
├── 01_documents/
│   ├── sample_docs/              # 5 ta namunaviy futbol hujjati (PDF, DOCX, TXT, MD) + .meta.json
│   └── my_documents/             # o'zingizning fayllaringiz (git'ga tushmaydi)
│
├── 02_document_loading/
│   ├── src/document_loading/
│   │   ├── step0_document.py     # Document dataclass
│   │   ├── step1_load.py         # 2.1 Load, PDF/DOCX/TXT/MD -> matn
│   │   ├── step2_metadata.py     # 2.2 Metadata, document_id, source, page, topic ...
│   │   └── step3_cleaning.py     # 2.3 Cleaning, ortiqcha bo'sh joy, ko'rinmas belgilar
│   ├── scripts/run_document_loading.py
│   └── tests/
│
├── 03_chunking/
│   ├── src/chunking/text_splitter.py      # token bo'yicha 500 / 50 chunk'lar
│   ├── scripts/run_chunking.py
│   ├── output/chunks.jsonl                # pipeline yaratadi (git'ga tushmaydi)
│   └── tests/
│
├── 04_embedding_model/
│   ├── src/embedding_model/embedder.py    # all-MiniLM-L6-v2 -> 384 o'lchamli vector
│   ├── scripts/run_embedding.py
│   └── tests/
│
└── 05_vector_database/
    ├── src/vector_database/qdrant_store.py   # id + vector + payload -> Qdrant
    ├── scripts/step1_run_vector_database.py   # butun pipeline + Qdrant'dagi point'ni ko'rsatadi
    ├── scripts/step2_inspect_collection.py    # collection'da nima saqlanganini ko'rsatadi
    └── tests/
```

Loyiha ildizidagi umumiy fayllar (ikkala pipeline ham ishlatadi):
[config/settings.py](../config/README.md), `.env`, `docker-compose.yml`, `requirements.txt`, `pytest.ini`.

## Kutubxonalar

| Kutubxona (`pip`) | Bosqich | Nima uchun |
|---|---|---|
| `pymupdf` | 02 | PDF sahifalarini o'qish |
| `python-docx` | 02 | DOCX paragraph va jadvallarini o'qish |
| `transformers` | 03 | tokenizer: matn → token'lar |
| `sentence-transformers` | 04 | embedding model: matn → 384 ta son (`torch` bilan o'rnatiladi) |
| `numpy` | 04, 05 | vector'lar bilan hisob-kitob |
| `qdrant-client` | 05 | Qdrant'ga yozish va o'qish |
| `python-dotenv` | config | `.env` faylini o'qish |
| `pytest` | tests | testlar |

Python'ning o'zida bor (o'rnatish shart emas): `pathlib`, `json`, `uuid`, `re`, `unicodedata`, `dataclasses`, `argparse`.

## Darsda: nazariya + amaliyot parallel

Har bir bosqich nazariyasidan keyin o'sha bosqich skriptini ishga tushiring (loyiha ildizidan):

| Bosqich | Nazariya | Amaliyot | Nima ko'rinadi |
|---|---|---|---|
| 01 Documents | [README](01_documents/README.md) | VS Code'da `01_documents/sample_docs/` papkasini ochish | fayllar, formatlar, `.meta.json` sidecar'lar |
| 02 Document Loading | [README](02_document_loading/README.md) | `python Indexing/02_document_loading/scripts/run_document_loading.py` | o'qilgan matnlar, metadata, tozalash oldin/keyin |
| 03 Chunking | [README](03_chunking/README.md) | `python Indexing/03_chunking/scripts/run_chunking.py --chunk-size 120 --overlap 20` | token'lar, chunk'lar, overlap |
| 04 Embedding Model | [README](04_embedding_model/README.md) | `python Indexing/04_embedding_model/scripts/run_embedding.py` | 384 ta son, norm = 1, ma'no yaqinligi |
| 05 Vector Database | [README](05_vector_database/README.md) | `python Indexing/05_vector_database/scripts/step1_run_vector_database.py` | Qdrant'dagi point: id + vector + payload |

Butun pipeline bitta buyruq bilan:

```bash
python Indexing/indexing_pipeline.py
python Indexing/indexing_pipeline.py --data-dir Indexing/01_documents/my_documents
```

## Tayyorgarlik (bir marta)

```bash
pip install -r requirements.txt
docker compose up -d qdrant        # 05-bosqich uchun. Dashboard: http://localhost:6333/dashboard
```

Docker bo'lmasa: `.env` faylida `QDRANT_LOCAL_PATH=qdrant_local`: Qdrant diskdagi papkada ishlaydi.
Batafsil: [qdrant_local/README.md](../qdrant_local/README.md).

## Testlar

```bash
pytest                                     # hammasi (Qdrant server kerak bo'lgan 2 ta test server bo'lmasa skip bo'ladi)
pytest -m "not slow and not integration"   # tezkor testlar (model va server'siz)
pytest Indexing/03_chunking                # faqat bitta bosqich testlari
```

## Mashqlar

1. **01:** `my_documents/` ga o'z PDF yoki DOCX faylingizni qo'ying va unga `.meta.json` sidecar yozing.
2. **02:** `my_documents/` ga `broken.pdf` nomli oddiy matn fayl yarating, pipeline to'xtamasdan xatoni hisobotda ko'rsatishini tekshiring.
3. **03:** `--chunk-size 120 --overlap 20` va `--chunk-size 500 --overlap 50` natijalarini solishtiring.
4. **04:** Nima uchun `chunk_size=500 > max_seq_length=256` ogohlantirishi chiqadi? `.env`da `TACTIQ_CHUNK_SIZE=256`, `TACTIQ_CHUNK_OVERLAP=25`, `QDRANT_COLLECTION=tactiq_256` qilib qayta ishga tushiring.
5. **05:** `step1_run_vector_database.py` ni ikki marta ishga tushiring, point'lar soni o'zgarmasligi kerak. Nima uchun?

## Keyingi pipeline bilan bog'liqlik

Retrieval & Generation pipeline'i `embedding_model.EmbeddingModel` va `vector_database.QdrantStore`'ni
shu papkadan **import qiladi**: foydalanuvchi savoli hujjatlar bilan **aynan bir xil** embedding model
orqali vector'ga aylantirilishi shart.
