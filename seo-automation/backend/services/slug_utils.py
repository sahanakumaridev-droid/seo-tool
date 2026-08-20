"""Canonical public article slugs: {keyword}-{city} → /web-design-san-diego."""
import re
from typing import Optional, Sequence


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", (text or "").lower()).strip("-")


def article_slug(keywords: Optional[Sequence[str]], city: str, fallback: str = "") -> str:
    """Build a live URL slug from the first target keyword + city.

    'web design' + San Diego → web-design-san-diego
    'web design san diego' + San Diego → web-design-san-diego (city not doubled)
    """
    kw = ""
    for item in keywords or []:
        if isinstance(item, str) and item.strip():
            kw = slugify(item)
            break
    loc = slugify(city)
    if kw and loc and loc not in kw:
        return f"{kw}-{loc}"
    if kw:
        return kw
    if loc:
        fb = slugify(fallback)
        return f"{fb}-{loc}" if fb and loc not in fb else loc
    return slugify(fallback)
