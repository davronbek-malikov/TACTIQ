# Indexing Pipeline (Data Ingestion)

TACTIQ'ning birinchi pipeline'i. U foydalanuvchi savol berishidan **oldin** ishlaydi va
futbol hujjatlarini Qdrant'da qidirish mumkin bo'lgan vector'larga aylantiradi.

```
Document Loading -> Text Cleaning -> Metadata -> Chunking -> Embedding Generation -> Qdrant Storage
```

## Papka tuzilishi

```text
indexing_pipeline/
├── README.md                        # shu fayl
├── src/indexing/
│   ├── document_loading/
│   │   ├── document.py              # Document dataclass — barcha bosqichlar shu obyektni uzatadi
│   │   └── loader.py                # 1. PDF, DOCX, TXT, MD -> Document
│   ├── text_cleaning/
│   │   └── cleaner.py               # 2. bo'sh joylar, control belgilar, Unicode
│   ├── metadata/
│   │   └── metadata_builder.py      # 3. document_id (uuid5), source, page, .meta.json
│   ├── chunking/
│   │   └── text_splitter.py         # 4. token bo'yicha 500 / 50 chunk'lar
│   ├── embeddings/
│   │   └── embedding_model.py       # 5. all-MiniLM-L6-v2 -> 384 o'lchamli vector
│   ├── vector_store/
│   │   └── qdrant_store.py          # 6. id + vector + payload -> Qdrant
│   └── pipeline.py                  # hamma bosqichlarni tartib bilan bog'laydi
├── scripts/
│   ├── ingest_documents.py          # butun pipeline'ni ishga tushirish
│   └── inspect_collection.py        # Qdrant'da nima saqlanganini ko'rish
├── notebooks/
│   └── indexing_pipeline.ipynb      # bosqichma-bosqich, har bir natijani ko'rib
└── tests/                           # har bir bosqich uchun alohida testlar
```

Loyiha ildizidagi umumiy fayllar (ikkala pipeline ham ishlatadi):
`config/settings.py`, `.env`, `docker-compose.yml`, `requirements.txt`, `data/`.

## Bosqichlar

| # | Bosqich | Fayl | Input -> Output |
|---|---|---|---|
| 1 | Document Loading | [loader.py](src/indexing/document_loading/loader.py) | papka -> `Document`'lar (PDF'da har sahifa alohida) |
| 2 | Text Cleaning | [cleaner.py](src/indexing/text_cleaning/cleaner.py) | `Document` -> matni tozalangan `Document` |
| 3 | Metadata | [metadata_builder.py](src/indexing/metadata/metadata_builder.py) | `Document` -> to'liq metadata'li `Document` |
| 4 | Chunking | [text_splitter.py](src/indexing/chunking/text_splitter.py) | `Document` -> `Chunk`'lar (chunk_id, document_id, text, metadata) |
| 5 | Embedding Generation | [embedding_model.py](src/indexing/embeddings/embedding_model.py) | chunk matnlari -> `(chunk_soni, 384)` numpy array |
| 6 | Qdrant Storage | [qdrant_store.py](src/indexing/vector_store/qdrant_store.py) | chunk'lar + vector'lar -> Qdrant point'lari |

## Ishga tushirish (loyiha ildizidan)

```bash
pip install -r requirements.txt
docker compose up -d qdrant                                          # Qdrant: http://localhost:6333/dashboard

python indexing_pipeline/scripts/ingest_documents.py --data-dir data/sample_docs
python indexing_pipeline/scripts/inspect_collection.py --limit 3

pytest                                                               # barcha testlar
pytest -m "not slow and not integration"                             # tezkor testlar (model va server'siz)
```

Docker bo'lmasa: `.env` faylida `QDRANT_LOCAL_PATH=qdrant_local` — Qdrant diskdagi papkada ishlaydi.

## Mashqlar

1. **Overlap'ni ko'rish.** Notebook'dagi mashq: `chunk_size=120, overlap=20` bilan 1-chunk oxiri va
   2-chunk boshini solishtiring.
2. **Nega ogohlantirish chiqadi?** Pipeline oxirida `chunk_size (500) > max_seq_length (256)` ogohlantirishi
   chiqadi. Sababini tushuntiring, keyin `.env`da `TACTIQ_CHUNK_SIZE=256`, `TACTIQ_CHUNK_OVERLAP=25` qilib,
   yangi collection nomi bilan (`QDRANT_COLLECTION=tactiq_256`) qayta ishga tushiring.
3. **Idempotency.** Pipeline'ni ikki marta ishga tushiring — point'lar soni o'zgarmasligi kerak. Nima uchun?
4. **Yangi hujjat.** `data/raw/` ga o'zingizning PDF/DOCX faylingizni va unga `.meta.json` sidecar qo'shing.
5. **Buzilgan fayl.** `data/raw/broken.pdf` nomli matn fayl yarating — pipeline to'xtamasdan xatoni hisobotda ko'rsatishini tekshiring.

## Keyingi pipeline bilan bog'liqlik

Retrieval & Generation pipeline (`retrieval_generation_pipeline/`, hali yaratilmagan) shu paketdan
`EmbeddingModel` va `QdrantStore`'ni **import qiladi**: foydalanuvchi savoli hujjatlar bilan
**aynan bir xil** embedding model orqali vector'ga aylantirilishi shart.
