# src/app: sahifalar

Next.js qoidasi: **papka = URL**, ichidagi `page.tsx` = o'sha sahifa.

| Fayl | URL | Nima ko'rsatadi | Backend |
|---|---|---|---|
| `layout.tsx` | hamma sahifa | `<html>`, shrift, `AppShell` (chap menyu) |: |
| `globals.css` | hamma sahifa | Tailwind + rang tokenlari (`--color-primary` ...) |: |
| `page.tsx` | `/` | Overview: Qdrant holati, hujjat/chunk soni, tarix, tavsiya savollar | `/api/system`, `/api/indexing/history` |
| `investigate/page.tsx` | `/investigate` | **RAG chat**: chapda manbalar, o'rtada savol-javob, o'ngda dalillar | `/api/investigate`, `/api/documents`, `/api/llms` |
| `knowledge/page.tsx` | `/knowledge` | hujjatlar jadvali, upload, indexing, tafsilot | `/api/documents...`, `/api/indexing/jobs` |
| `reports/page.tsx` | `/reports` | saqlangan javoblar (brauzer xotirasida), Markdown eksport |: |
| `settings/page.tsx` | `/settings` | Qdrant rejimi, LLM'lar holati, sozlamalar | `/api/system`, `/api/llms` |
| `matches/page.tsx` | `/matches` | rejada (Coming soon) + video komponent namunasi | `/api/documents` |
| `players/page.tsx` | `/players` | rejada (Coming soon) | `/api/documents` |
| `favicon.ico` |: | brauzer tab ikonkasi |: |

## Investigate sahifasi qanday ishlaydi

```
Composer (savol + LLM)  ->  ask()  ->  api.investigate()  ->  backend 7 bosqich
                                         |
                    javob  ->  TurnView (matn + [1] + ProgressSteps)
                    dalil  ->  EvidencePanel (chunk'lar, score)
```

`[1]` bosilsa → `cite()` → o'ng paneldagi 1-dalil ochiladi.

## Kutubxonalar

```tsx
import { useEffect, useMemo, useState } from "react";  // state, yuklanganda bir marta ishlash, hisoblangan qiymat
import Link from "next/link";                           // sahifalar orasida tez o'tish
import { Search, Upload } from "lucide-react";          // ikonkalar
```
