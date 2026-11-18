# UI frontend: Next.js

Brauzerda ko'rinadigan qism. Faqat **backend** (`http://localhost:8000`) bilan gaplashadi: Qdrant yoki LLM'ga to'g'ridan-to'g'ri emas.

```
sahifa (src/app)  ->  komponent (src/components)  ->  api.ts (src/lib)  --fetch-->  backend :8000
```

## Papkalar

| Papka | Nima | README |
|---|---|---|
| `src/app/` | sahifalar: har bir papka = bitta URL (`/investigate`, `/knowledge` ...) | [src/app](src/app/README.md) |
| `src/components/` | qayta ishlatiladigan bo'laklar: tugma, karta, dalil kartasi ... | [src/components](src/components/README.md) |
| `src/lib/` | backend bilan aloqa, turlar, yordamchi funksiyalar | [src/lib](src/lib/README.md) |

## Ildizdagi fayllar

| Fayl | Nima |
|---|---|
| `package.json` | kutubxonalar ro'yxati va buyruqlar (`npm run dev`) |
| `package-lock.json` | kutubxonalarning aniq versiyalari (avtomatik) |
| `next.config.ts` | Next.js sozlamasi (Tailwind loader) |
| `tsconfig.json` | TypeScript sozlamasi; `@/` = `src/` |
| `eslint.config.mjs` | kod sifati tekshiruvi (`npm run lint`) |
| `.env.example` | `NEXT_PUBLIC_API_URL`: backend manzili |
| `AGENTS.md` | AI yordamchilar uchun eslatma (`next dev` o'zi yozadi) |

## Kutubxonalar (`package.json`)

```jsonc
"next": "16.4.6",            // React framework: sahifalar (papka = URL), server, build
"react": "19.3.0",           // UI komponentlar: useState, useEffect
"react-dom": "19.3.0",       // React'ni brauzerga chizadi
"lucide-react": "^1.70.0",   // ikonkalar: <Search />, <Upload /> ...
"tailwindcss": "4.3.3",      // CSS class'lar: "rounded-xl p-4 text-sm"
"typescript": "^5",          // JavaScript + turlar (xatolarni oldindan topadi)
"eslint": "^9"               // kod sifati
```

## Asosiy tushunchalar

- **Komponent**: HTML qaytaradigan funksiya: `function Card() { return <div>...</div> }`.
- **`"use client"`**: komponent brauzerda ishlaydi (tugma bosish, state).
- **`useState`**: o'zgaruvchan qiymat; o'zgarsa sahifa qayta chiziladi.
- **`useApi`** ([src/lib/use-api.ts](src/lib/use-api.ts)): backend'dan ma'lumot: `data`, `loading`, `error`.

## Ishga tushirish

```bash
cd UI/frontend
npm install        # faqat birinchi marta (node_modules/)
npm run dev        # http://localhost:3000
npm run lint       # tekshiruv
npm run build      # production build + TypeScript tekshiruvi
```
