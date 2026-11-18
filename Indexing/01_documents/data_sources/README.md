# data_sources: haqiqiy futbol datasini hujjatga aylantirish

**Muammo:** `sample_docs` dagi 5 ta hujjatda umumiy taktika bor, uni oddiy LLM ham biladi.
**Yechim:** ochiq va bepul futbol datasini yuklab, undan **aniq raqamli** matnli hisobotlar yasaymiz
(xG, pressing, PPDA, off-ball run, tezlik ...). Bunday raqamlarni LLM yodda saqlay olmaydi: ularni RAG beradi.

```
Ochiq data (JSON/CSV)  ->  data_sources/*.py  ->  football_data/*.md + .meta.json  ->  Indexing 02 -> 05
event, tracking            hisoblash + matn        oddiy hujjatlar                      boshqa fayllar kabi
```

## Manbalar

| Manba | Litsenziya | Nima olindi | Hujjatlar |
|---|---|---|---|
| [StatsBomb Open Data](https://github.com/statsbomb/open-data) | bepul, "StatsBomb" deb ko'rsatish shart | World Cup 2022 (+360), Euro 2024, Copa América 2024, AFCON 2023, Bundesliga 2023/24 (Leverkusen) | 1473 |
| [Wyscout public dataset](https://figshare.com/collections/Soccer_match_event_dataset/4415000) | CC BY 4.0 | World Cup 2018, Euro 2016 (event), 5 ta top liga 2017/18 (jadval + to'purarlar) | 178 |
| [SkillCorner Open Data](https://github.com/SkillCorner/opendata) | MIT | A-League 2024/25: 20 o'yin (off-ball run, pressing, phases of play), 267 o'yinchi jismoniy profili | 301 |

**Olinmagan manbalar** (sabab: ochiq data yo'q yoki qoidalari avtomatik yig'ishni taqiqlaydi):
Hudl, Wyscout platformasi, DataMB, FootballCritic: pullik/yopiq; FBref, Sofascore, Understat: rasmiy API yo'q,
sayt qoidalari scraping'ni cheklaydi. Litsenziya bo'lsa (klub obunasi), xuddi shu usulda qo'shiladi.

## Hujjat turlari (`document_type` sidecar'da)

| `document_type` | Bitta hujjat = | Misol savol |
|---|---|---|
| `*_match_report` | bitta o'yin: natija, gollar, tarkib, jamoa statistikasi | "Argentina vs France finalida kim ko'proq pressing qildi?" |
| `*_team_profile` | jamoa turnirda: natijalar, uslub, formatsiyalar | "Spain Euro 2024 da qaysi formatsiyada o'ynadi?" |
| `*_player_profile` | o'yinchi turnirda/mavsumda | "Messi World Cup 2022 da nechta progressive pas berdi?" |
| `*_leaderboard` | turnir bo'yicha top-10 ro'yxatlar | "Euro 2024 da eng ko'p xG kimda?" |
| `wyscout_league_table` | liga yakuniy jadvali | "Serie A 2017/18 da Napoli nechta ochko yig'di?" |

Prefiks manbani bildiradi: `statsbomb_`, `wyscout_`, `skillcorner_`.

## Fayllar

| Fayl | Nima qiladi |
|---|---|
| `common.py` | `download()` (kesh bilan), `write_document()` (.md + .meta.json), `slug()`, `pct()` |
| `statsbomb.py` | event'lar → xG, pressing, PPDA, progressive pass, 360 (passer atrofidagi raqiblar) |
| `wyscout.py` | event tag'lari (101 gol, 302 key pass, 1801 aniq) → o'yin/jamoa/top ro'yxat; liga jadvallari |
| `skillcorner.py` | dynamic events + mavsum CSV'lari → off-ball run, pressing, jismoniy profil |
| `.cache/` | xom data (~1.3 GB), git'ga tushmaydi |

## Muhim g'oya: chunk'ga chidamli matn

Chunking matnni token bo'yicha kesadi, sarlavha chunk'dan tushib qolishi mumkin. Shuning uchun **har bir gap
o'z kontekstini o'zi olib yuradi**:

```
❌  xG 2.76 from 20 shots.
✅  Argentina against France (FIFA World Cup 2022, Final, 2022-12-18): xG 2.76 from 20 shots ...
```

Shu sabab `.env` da `TACTIQ_CHUNK_SIZE=256`, `TACTIQ_CHUNK_OVERLAP=25`: embedding model (MiniLM) baribir
faqat 256 token o'qiydi; katta chunk'ning qolgan qismi qidiruvda "ko'rinmaydi".

## Kutubxonalar (hammasi Python'ning o'zida: o'rnatish shart emas)

```python
import urllib.request   # faylni internetdan yuklash
import json             # StatsBomb/Wyscout JSON fayllari
import csv              # SkillCorner CSV fayllari
import zipfile          # Wyscout events.zip ichidan o'qish
import math             # math.dist: 360 data'da masofa
from collections import Counter, defaultdict  # sanash va jamlash
```

## Ishga tushirish (loyiha ildizidan)

```bash
cd Indexing/01_documents/data_sources
python statsbomb.py                 # ~10 daqiqa birinchi marta (yuklash), keyin keshdan
python statsbomb.py --only 43/106   # faqat World Cup 2022
python wyscout.py
python skillcorner.py
cd ../../..
python Indexing/indexing_pipeline.py --data-dir Indexing/01_documents/football_data
```

Yoki UI: **Knowledge → Football data → Index**.

## Halollik

- Har bir hujjatda manba va litsenziya yozilgan (`Data source: ...`).
- Daqiqalar taxminiy (almashtirishlardan hisoblanadi): matnda "about" deyilgan.
- 360 ko'rsatkichlari faqat kamera ko'rgan maydon bo'yicha: matnda "visible area only".
- Bundesliga 2023/24 da faqat Leverkusen o'yinlari bor: profillarda o'yinlar soni ko'rsatilgan.
