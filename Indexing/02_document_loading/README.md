# 02 — Document Loading

**Fayllardan matnni o'qish** — va har bir matnga "pasport" (metadata) biriktirib, uni tozalash.

## Nazariya

Bu bosqich uchta kichik qadamdan iborat (`src/document_loading/` ichida):

| Qadam | Fayl | Nima qiladi |
|---|---|---|
| 2.1 Load | [step1_load.py](src/document_loading/step1_load.py) | Papkadagi fayllarni topadi va matnni o'qiydi. PDF → har sahifa alohida `Document` (sahifa raqami saqlanadi). Buzilgan fayl pipeline'ni to'xtatmaydi — xato hisobotga yoziladi. |
| 2.2 Metadata | [step2_metadata.py](src/document_loading/step2_metadata.py) | `document_id` (uuid5 — har safar bir xil), `source`, `page`, `file_type` + sidecar'dagi `topic`, `language` ... |
| 2.3 Text Cleaning | [step3_cleaning.py](src/document_loading/step3_cleaning.py) | Ortiqcha bo'sh joylar, bo'sh qatorlar, ko'rinmas belgilarni olib tashlaydi. `4-3-3`, `xG`, `Gündoğan` o'zgarmaydi. |

[step0_document.py](src/document_loading/step0_document.py) — uchala qadam bir-biriga uzatadigan `Document(text, metadata)` dataclass.

**Metadata nima uchun kerak?**
- **Citation:** javob ostida "manba: counterpressing.pdf, 2-sahifa".
- **Metadata filtering:** "faqat `topic = high_pressing` hujjatlaridan qidir".
- **Provenance:** har bir dalil qayerdan kelganini bilish.

## Amaliyot

```bash
python Indexing/02_document_loading/scripts/run_document_loading.py
```

Ko'rinadi: har bir o'qilgan matn (fayl, sahifa, belgilar soni) → birinchi hujjatning to'liq metadata'si →
tozalashdan oldin/keyin farq.

## Testlar

```bash
pytest Indexing/02_document_loading
```

**Keyingi bosqich:** [03 — Chunking](../03_chunking/README.md)
