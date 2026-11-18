# src/components: qayta ishlatiladigan bo'laklar

## ui/: umumiy dizayn bo'laklari

| Fayl | Nima |
|---|---|
| `button.tsx` | `<Button variant="primary">`: 4 xil ko'rinish, `loading` holati |
| `card.tsx` | `Card`, `CardHeader`, `PageHeader`: oq ramkali blok |
| `badge.tsx` | `Badge` (rangli yorliq), `StatusDot` (yashil/qizil nuqta) |
| `fields.tsx` | `Field`, `Input`, `Select`: forma elementlari |
| `states.tsx` | `EmptyState`, `LoadingState`, `ErrorState`: bo'sh / yuklanmoqda / xato |
| `planned.tsx` | `PlannedNotice`: "Coming soon" va nima kerakligi |

## layout/: sahifa ramkasi

| Fayl | Nima |
|---|---|
| `nav.ts` | menyu bandlari: Overview, Investigate, Knowledge ... |
| `app-shell.tsx` | chap menyu + tepa panel (Qdrant holati) + mobil menyu |

## investigate/: RAG chat

| Fayl | Nima | RAG bosqichi |
|---|---|---|
| `composer.tsx` | savol yozish, LLM tanlash, RAG / LLM only | 01, 06 |
| `knowledge-panel.tsx` | chap panel: collection, hujjat, topic, til filter'lari | 03 (filter) |
| `turn-view.tsx` | bitta savol + javob kartasi | 07 |
| `answer-text.tsx` | javobdagi `[1]` → bosiladigan tugma | 07 (manba) |
| `progress-steps.tsx` | 7 bosqich: done / skipped / failed + vaqt (ms) | 01–07 |
| `evidence-panel.tsx` | o'ng panel: topilgan chunk'lar | 04 |

## knowledge/: hujjatlar

| Fayl | Nima | Indexing bosqichi |
|---|---|---|
| `upload-card.tsx` | fayl tashlash (drag & drop) + metadata | 01 |
| `indexing-card.tsx` | "Index" tugmasi, job holati (har 1 s so'raladi) | 02–05 |
| `document-detail.tsx` | tafsilot: metadata, sahifa matni, chunk'lar; tahrir/o'chirish | 02, 03 |

## evidence/, video/

| Fayl | Nima |
|---|---|
| `evidence/evidence-card.tsx` | bitta dalil: manba, sahifa, score, matn; 6 ta dalil kategoriyasi |
| `video/video-workspace.tsx` | kelajakdagi video tahlil uchun tayyor komponent (hozir ma'lumotsiz) |

## Kutubxonalar

```tsx
import { useState, type ReactNode } from "react";   // state; ReactNode: ichiga har qanday JSX
import { LoaderCircle, FileText } from "lucide-react"; // ikonkalar
import { cn } from "@/lib/format";                   // class'larni birlashtirish: cn("p-4", active && "bg-subtle")
```
