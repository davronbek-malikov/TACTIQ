# 01: Documents

**PDF, TXT, DOCX va boshqa fayllar**: Indexing pipeline'ning kirishi (input).

## Nazariya

- RAG model bilmaydigan bilimni **hujjatlardan** oladi: taktik hisobotlar, scouting report'lar, o'yin tahlillari.
- Hujjat formatlari turlicha: PDF (sahifalar bor), DOCX (paragraph va jadvallar), TXT/Markdown (oddiy matn).
- Har bir hujjat yonida ixtiyoriy **sidecar** fayl bo'lishi mumkin: `high_pressing.docx.meta.json`.
  Unda odam yozib bergan metadata turadi (`document_type`, `topic`, `language`, `match_id` ...).
  Sidecar bo'lmasa, bu maydonlar `None` bo'ladi, TACTIQ metadata'ni **o'ylab topmaydi**.

## Papkalar

| Papka | Nima uchun |
|---|---|
| `sample_docs/` | 5 ta namunaviy hujjat: high pressing (DOCX), low block (TXT), counterpressing (PDF, 2 sahifa), build-up play (MD), defensive transitions (MD). **Ta'limiy namuna**: haqiqiy o'yin statistikasi yo'q. |
| `my_documents/` | O'zingizning fayllaringiz. Git'ga tushmaydi. |

`low_block.txt` ataylab "iflos" yozilgan (ortiqcha bo'sh joylar), 02-bosqichdagi tozalashni ko'rsatish uchun.
`build_up_play.md` eng uzun hujjat, 03-bosqichda bir nechta chunk'ga bo'linadi.

## Amaliyot

VS Code'da `sample_docs/` papkasini oching: 5 ta hujjat va har birining yonidagi `.meta.json` faylni ko'ring.
Bitta sidecar'ni ochib, ichidagi `topic` va `language` maydonlarini tekshiring.

Sidecar namunasi (`<fayl>.meta.json`):

```json
{ "document_type": "tactical_report", "topic": "high_pressing", "language": "en",
  "match_id": null, "team_id": null, "player_id": null }
```

**Keyingi bosqich:** [02, Document Loading](../02_document_loading/README.md)
