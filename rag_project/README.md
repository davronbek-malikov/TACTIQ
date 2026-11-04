# TACTIQ — RAG project (Local LLM + Cloud LLM)

Bitta bilim bazasi (Qdrant), ikki xil "miya": **local LLM** (Ollama / o'zimizning model) va **cloud LLM** (API).
Maqsad: RAG'ning kuchini jonli ko'rsatish — kichik local model ham RAG bilan to'g'ri javob beradi.

```
rag_project/
  config.py                         # barcha sozlamalar (chunk size, model, Qdrant)
  data/raw/<department>/...         # manba hujjatlar (PDF, TXT, MD, DOCX)
  indexing_pipeline/                # 1-pipeline — Lesson 5
    data_loading/                   #   1. Load + metadata (source, page, department, language)
    chunking/                       #   2. Fixed-size chunking (token: 500 / 50)
    embedding/                      #   3. Qwen3-Embedding-0.6B -> 1024-dim vector
    storing/                        #   4. Qdrant: collection, payload, upsert
    run_indexing.py                 #   Load -> metadata -> chunk -> embed -> store
  retrieval_generation_pipeline/    # 2-pipeline — keyingi dars
```

## Ishga tushirish

```bash
cd rag_project
pip install -r requirements.txt
python -m indexing_pipeline.run_indexing --recreate
python -m indexing_pipeline.run_indexing --test-query "OASIS Pro narxi qancha?"
```

Qdrant default holatda **local mode**da ishlaydi (`qdrant_db/` papkasi, Docker kerak emas).
Docker yoki Qdrant Cloud uchun `.env.example` -> `.env` nusxa oling va `QDRANT_URL` ni to'ldiring.

## Darsda sinab ko'rish uchun tajribalar

1. `--chunk-size 150 --overlap 20 --recreate` bilan qayta index qiling va `--test-query "Ta'til necha kun?"`
   natijasini 500/50 bilan solishtiring (katta chunk'da mavzular aralashib, score pasayadi).
2. `data/raw/sales/narxlar.docx` dagi narxni o'zgartiring -> qayta index -> javob darhol yangilanadi.
   Model qayta o'qitilmadi — RAG'ning asosiy afzalligi.
3. Pipeline'ni ikki marta ishga tushiring: point soni o'zgarmaydi (deterministic chunk ID + upsert).
4. `data/raw/` ga yangi bo'lim papkasini qo'shing (masalan `finance/`) — `department` metadata avtomatik.

Namuna hujjatlar (OASIS MChJ) — o'ylab topilgan kompaniya, faqat dars uchun.
