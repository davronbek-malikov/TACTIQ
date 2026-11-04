"""Metadata: har bir Document'ga "u qayerdan keldi?" degan ma'lumotni biriktirish.

Metadata keyinchalik ikki joyda ishlaydi:
  * metadata filtering — "faqat HR bo'limi hujjatlaridan qidir" (Qdrant payload filter)
  * citation          — javob ostida "manba: narxlar.pdf, 2-sahifa" deb ko'rsatish
"""

from datetime import date
from pathlib import Path

from config import DEFAULT_LANGUAGE


def build_metadata(
    path: Path,
    data_dir: Path,
    page: int | None = None,
    language: str = DEFAULT_LANGUAGE,
) -> dict:
    """Fayl yo'lidan metadata yasaydi.

    data/raw/hr/ish_tartibi.txt  ->  department = "hr"
    data/raw/narxlar.pdf          ->  department = "general"
    """
    relative = path.relative_to(data_dir)
    department = relative.parts[0] if len(relative.parts) > 1 else "general"

    return {
        "source": path.name,                 # fayl nomi (citation uchun)
        "file_type": path.suffix.lstrip(".").lower(),
        "page": page,                        # PDF uchun sahifa raqami, boshqalarda None
        "department": department,            # metadata filtering uchun
        "language": language,
        "indexed_at": date.today().isoformat(),
    }
