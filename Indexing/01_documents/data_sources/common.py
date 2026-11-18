"""
common — barcha data manbalari uchun umumiy yordamchilar: yuklab olish (kesh bilan) va hujjat yozish.

Har bir manba skripti (statsbomb.py, wyscout.py, skillcorner.py) xom data'ni yuklab,
undan oddiy matnli .md hisobot + .meta.json sidecar yasaydi. Keyin Indexing pipeline
ularni boshqa hujjatlar kabi o'qiydi (02 -> 05).
"""

import json
import time
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
CACHE_DIR = HERE / ".cache"                       # xom data (git'ga tushmaydi)
OUTPUT_DIR = HERE.parent / "football_data"        # tayyor hujjatlar -> indexing shu papkani o'qiydi


def download(url: str, name: str) -> Path:
    """URL'ni keshga yuklaydi. Fayl bor bo'lsa — qayta yuklamaydi."""
    path = CACHE_DIR / name
    if path.exists() and path.stat().st_size > 0:
        return path
    path.parent.mkdir(parents=True, exist_ok=True)
    for attempt in range(3):                      # internet uzilsa — 3 marta urinadi
        try:
            request = urllib.request.Request(url, headers={"User-Agent": "tactiq-data-loader"})
            with urllib.request.urlopen(request, timeout=120) as response:
                path.write_bytes(response.read())
            return path
        except OSError:
            if attempt == 2:
                raise
            time.sleep(2)
    return path


def load_json(url: str, name: str):
    """Yuklaydi (kesh bilan) va JSON sifatida o'qiydi."""
    with download(url, name).open(encoding="utf-8") as file:
        return json.load(file)


def slug(text: str) -> str:
    """'FIFA World Cup 2022' -> 'fifa_world_cup_2022' (fayl nomi uchun)."""
    return "".join(c if c.isalnum() else "_" for c in text.lower()).strip("_").replace("__", "_")


def write_document(folder: str, name: str, text: str, metadata: dict) -> Path:
    """<folder>/<name>.md + <name>.md.meta.json yozadi (02 Metadata shu sidecar'ni o'qiydi)."""
    path = OUTPUT_DIR / folder / f"{name}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.strip() + "\n", encoding="utf-8")
    # 02 Metadata faqat 6 ta kalitni o'qiydi -> manba nomi document_type ichiga: "statsbomb_match_report"
    sidecar = {
        "document_type": f"{metadata['data_source']}_{metadata['document_type']}",
        "topic": metadata.get("topic"),
        "language": "en",
        **{key: metadata.get(key) for key in ("match_id", "team_id", "player_id")},
    }
    path.with_name(path.name + ".meta.json").write_text(json.dumps(sidecar, indent=2), encoding="utf-8")
    return path


def pct(part: float, total: float) -> str:
    """Foiz: 0 ga bo'lishdan himoya."""
    return f"{100 * part / total:.0f}%" if total else "n/a"
