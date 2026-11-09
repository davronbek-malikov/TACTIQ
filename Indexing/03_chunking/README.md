# 03 — Chunking

**Matnni kichik qismlarga bo'lish.** Kod: [text_splitter.py](src/chunking/text_splitter.py)

## Nazariya

**Nima uchun bo'lamiz?**
1. Embedding model bir vaqtda cheklangan token'ni ko'radi (`all-MiniLM-L6-v2` — 256 token).
2. Kichik chunk = aniqroq ma'no: bitta chunk — bitta g'oya.
3. Keyinchalik LLM'ga butun hujjat emas, faqat kerakli chunk'lar beriladi.

**Fixed-size chunking**, `chunk_size = 500`, `overlap = 50` (token'da):

```
token'lar: [0 ............ 499]
                       [450 ............ 949]
                                      [900 ...... oxiri]
           |<- chunk_size ->|
                       |<->| overlap: 50 token ikkala chunk'da ham bor
step = chunk_size - overlap = 450
```

**Overlap** — muhim gap ikki chunk chegarasida bo'linib qolsa, kamida bittasida to'liq saqlanadi.

**Token** — model matnni so'zlarga emas, token'larga bo'lib o'qiydi:
`"Counterpressing"` → `['counter', '##pressing']`. Shuning uchun chunk'ni embedding model'ning **o'z tokenizer'i** bilan o'lchaymiz.

Har bir chunk: `chunk_id` (barqaror UUID), `document_id`, `text` (asl matndan aynan kesilgan), `metadata` (+ `chunk_index`, `token_count`).

## Amaliyot

```bash
python Indexing/03_chunking/scripts/run_chunking.py                          # 500 / 50
python Indexing/03_chunking/scripts/run_chunking.py --chunk-size 120 --overlap 20   # overlap aniq ko'rinadi
```

Ko'rinadi: window matematikasi → token'lar → har bir chunk (manba, sahifa, token soni, id) → 1-chunk oxiri va 2-chunk boshi (overlap).

Butun pipeline ishga tushganda chunk'lar `output/chunks.jsonl` ga ham yoziladi — ochib ko'rish mumkin.

## Testlar

```bash
pytest Indexing/03_chunking
```

**Keyingi bosqich:** [04 — Embedding Model](../04_embedding_model/README.md)
