"""
Rank Tracking — built from PUBLISHED SEO content (/p/{slug} pages), not the
onboarding website domain.

Keywords + URLs come from saved PageRecord seo_blocks. Position history is
hash-seeded (no live SERP vendor configured) so the same published page always
gets a stable trend line.
"""
import hashlib
import random
import re
from datetime import date, timedelta
from typing import Any, Dict, Iterable, List, Optional, Tuple

from models.schemas import RankingMetric, RankingPoint, RankingResult

_HISTORY_DAYS = 90
_HISTORY_STEP_DAYS = 7


def _seed(text: str) -> int:
    return int(hashlib.md5(text.strip().lower().encode()).hexdigest(), 16)


def _history_for(keyword: str, page_key: str, end_position: int) -> list[RankingPoint]:
    rng = random.Random(_seed(f"{keyword}|{page_key}|history"))
    n_points = _HISTORY_DAYS // _HISTORY_STEP_DAYS
    start = max(1, min(50, end_position + rng.randint(-8, 8)))
    points = []
    pos = start
    today = date.today()
    for i in range(n_points):
        day = today - timedelta(days=(n_points - 1 - i) * _HISTORY_STEP_DAYS)
        if i == n_points - 1:
            pos = end_position
        else:
            pos = max(1, min(60, pos + rng.randint(-2, 2)))
        points.append(RankingPoint(date=day.isoformat(), position=pos))
    return points


def _block_dict(raw: Any) -> Dict[str, Any]:
    if isinstance(raw, dict):
        return raw
    if hasattr(raw, "model_dump"):
        return raw.model_dump()
    return {}


def _keywords_from_block(block: Dict[str, Any]) -> List[Tuple[str, int]]:
    """
    Return (keyword, priority) pairs from a published SEO block.
    Lower priority number = more important (focus first).
    Never uses the page title as a keyword (too long / not query-like).
    """
    out: List[Tuple[str, int]] = []
    focus = (block.get("focus_keyword") or "").strip()
    if focus:
        out.append((focus, 0))

    kws = block.get("keywords") or {}
    if isinstance(kws, dict):
        primary = (kws.get("primary") or "").strip()
        if primary:
            out.append((primary, 1))
        for i, kw in enumerate((kws.get("secondary") or [])[:4]):
            if isinstance(kw, str) and kw.strip():
                out.append((kw.strip(), 2 + i))
        for i, kw in enumerate((kws.get("near_me") or [])[:2]):
            if isinstance(kw, str) and kw.strip():
                out.append((kw.strip(), 20 + i))
        for i, kw in enumerate((kws.get("long_tail") or [])[:2]):
            if isinstance(kw, str) and kw.strip():
                out.append((kw.strip(), 30 + i))

    for i, kw in enumerate((block.get("secondary_keywords") or [])[:4]):
        if isinstance(kw, str) and kw.strip():
            out.append((kw.strip(), 40 + i))

    # Fallback when the block has no keyword fields yet
    if not out:
        biz = (block.get("business_type") or "").strip()
        city = (block.get("city") or "").strip()
        if biz and city:
            out.append((f"{biz} {city}".strip(), 50))
            out.append((f"best {biz} in {city}".strip(), 51))
            out.append((f"{biz} near me".strip(), 52))

    # Drop obviously non-query strings
    cleaned: List[Tuple[str, int]] = []
    for kw, pri in out:
        k = kw.strip()
        if len(k) < 3 or len(k) > 70:
            continue
        if k.endswith(",") or k.count(" ") > 10:
            continue
        cleaned.append((k, pri))
    return cleaned


def _page_url(slug: str, block: Dict[str, Any], public_base: str) -> str:
    wp = (block.get("wp_post_url") or "").strip()
    if wp and "example.com" not in wp.lower():
        return wp
    base = (public_base or "").rstrip("/")
    if base and slug:
        return f"{base}/p/{slug}"
    if slug:
        return f"/p/{slug}"
    return ""


def _metric_for(keyword: str, page_key: str, url: str, quality_hint: float = 0.5) -> RankingMetric:
    """
    Stable position from keyword + published page. Better SEO quality hints
    (readability / density) bias toward stronger ranks.
    """
    rng = random.Random(_seed(f"{keyword}|{page_key}|rank"))
    # quality_hint 0..1 → prefer positions in top 20 for stronger pages
    ceiling = int(18 + (1.0 - quality_hint) * 30)  # 18..48
    floor = max(1, int(1 + (1.0 - quality_hint) * 6))
    position = rng.randint(floor, max(floor, ceiling))
    previous_position = max(1, min(60, position + rng.randint(-6, 6)))
    volume = rng.choice([rng.randint(40, 400), rng.randint(400, 2500), rng.randint(2500, 12000)])
    return RankingMetric(
        keyword=keyword,
        position=position,
        previous_position=previous_position,
        volume=volume,
        url=url,
        history=_history_for(keyword, page_key, position),
    )


def _quality_hint(block: Dict[str, Any]) -> float:
    score = 0.45
    try:
        r = float(block.get("readability_score") or 0)
        if r > 0:
            score = min(0.95, max(0.2, r / 100.0))
    except (TypeError, ValueError):
        pass
    if block.get("focus_keyword"):
        score = min(0.98, score + 0.08)
    if block.get("featured_image_url"):
        score = min(0.98, score + 0.04)
    faqs = block.get("faqs") or []
    if isinstance(faqs, list) and len(faqs) >= 3:
        score = min(0.98, score + 0.05)
    return score


class MockRankProvider:
    async def track(
        self,
        business_type: str,
        location: str,
        website: str = "",
        pages: Optional[Iterable[Any]] = None,
        public_base: str = "",
    ) -> RankingResult:
        """
        Build rankings from published SEO pages.
        `pages` should be PageRecord-like objects with .slug, .seo_block, .city, .business_type.
        Falls back to empty result when nothing is published (never invent website paths).
        """
        rows = list(pages or [])
        if not rows:
            return RankingResult(business_type=business_type, location=location, keywords=[])

        # Optional filter: prefer pages matching the active project niche when set
        bt = (business_type or "").strip().lower()
        if bt:
            matched = [
                r for r in rows
                if bt in (getattr(r, "business_type", "") or "").lower()
                or bt in str((_block_dict(getattr(r, "seo_block", None)).get("business_type") or "")).lower()
            ]
            if matched:
                rows = matched

        # keyword → (priority, metric) — keep best (lowest priority) owner page
        best: Dict[str, Tuple[int, RankingMetric]] = {}

        for row in rows:
            slug = (getattr(row, "slug", None) or "").strip()
            block = _block_dict(getattr(row, "seo_block", None))
            if not slug and block.get("slug"):
                slug = str(block.get("slug")).strip()
            url = _page_url(slug, block, public_base)
            if not url:
                continue
            page_key = slug or url
            quality = _quality_hint(block)
            for keyword, priority in _keywords_from_block(block):
                key = keyword.strip().lower()
                if not key:
                    continue
                metric = _metric_for(keyword.strip(), page_key, url, quality)
                prev = best.get(key)
                if prev is None or priority < prev[0]:
                    best[key] = (priority, metric)

        metrics = [m for _, m in sorted(best.values(), key=lambda x: (x[1].position, x[1].keyword.lower()))]
        # Prefer focus/primary terms first in the UI — already sorted by position,
        # but cap so a large city batch stays usable.
        return RankingResult(business_type=business_type, location=location, keywords=metrics[:120])
