# src/lib: backend bilan aloqa va yordamchilar

| Fayl | Nima |
|---|---|
| `api.ts` | **backend bilan barcha aloqa shu yerda**: `api.investigate()`, `api.documents()`, `api.upload()` ... |
| `types.ts` | javob shakllari (`InvestigateResponse`, `Evidence` ...): `UI/backend/schemas.py` bilan bir xil |
| `use-api.ts` | `useApi(() => api.system())` → `{ data, loading, error, reload }` |
| `reports.ts` | saqlangan javoblar: brauzerning `localStorage`'ida; Markdown'ga aylantirish |
| `format.ts` | `cn()` (class'lar), `formatBytes()`, `formatDate()`, `formatTimestamp()` |

## So'rov qanday ketadi

```ts
api.investigate({ question, llm: "gemini", mode: "rag" })
  -> fetch("http://localhost:8000/api/investigate", { method: "POST", body: JSON })
  -> backend: 01 ... 07
  -> InvestigateResponse { answer, evidence[], steps[] }
```

Backend ishlamasa: `Backend is not reachable at ... Start it with: python UI/backend/main.py`.

## Kutubxonalar

```ts
fetch(url, init)        // brauzerda bor: HTTP so'rov (o'rnatish shart emas)
FormData                // fayl yuklash uchun (upload)
localStorage            // brauzer xotirasi (reports)
process.env.NEXT_PUBLIC_API_URL   // .env.local dagi backend manzili
```
