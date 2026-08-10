"""
mock_rank_data.py — Rank Tracking data, seeded from the REAL project's
business type + location (not live SERP scraping — there's no configured
rank-tracking vendor). Same honesty level as the existing Keyword Research
mock: real input -> stable, topically-relevant, hash-seeded output.
"""
import hashlib
import random
import re
from datetime import date, timedelta

from models.schemas import RankingMetric, RankingPoint, RankingResult
from services.keyword_service import generate_keywords

_HISTORY_DAYS = 90
_HISTORY_STEP_DAYS = 7


def _seed(text: str) -> int:
    return int(hashlib.md5(text.strip().lower().encode()).hexdigest(), 16)


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def _history_for(keyword: str, location: str, end_position: int) -> list[RankingPoint]:
    rng = random.Random(_seed(f"{keyword}|{location}|history"))
    n_points = _HISTORY_DAYS // _HISTORY_STEP_DAYS
    # Correlated random walk ending at `end_position` so the line reads as a
    # believable trend rather than pure noise.
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


def _metric_for(keyword: str, location: str, website: str = "") -> RankingMetric:
    rng = random.Random(_seed(f"{keyword}|{location}"))
    position = rng.randint(1, 45)
    previous_position = max(1, min(60, position + rng.randint(-6, 6)))
    volume = rng.choice([rng.randint(20, 300), rng.randint(300, 2000), rng.randint(2000, 9000)])
    path = f"/{_slug(keyword)}"
    domain = website.strip().replace("https://", "").replace("http://", "").strip("/")
    url = f"https://{domain}{path}" if domain else path
    return RankingMetric(
        keyword=keyword,
        position=position,
        previous_position=previous_position,
        volume=volume,
        url=url,
        history=_history_for(keyword, location, position),
    )


class MockRankProvider:
    async def track(self, business_type: str, location: str, website: str = "") -> RankingResult:
        city = location.split(",")[0].strip() if location else ""
        state = location.split(",")[1].strip() if "," in location else ""
        keywords_set = await generate_keywords(business_type, city or location, state)

        tracked = [keywords_set.primary] + keywords_set.secondary[:5] + keywords_set.near_me[:3]
        seen = set()
        unique_keywords = []
        for kw in tracked:
            key = kw.strip().lower()
            if key and key not in seen:
                seen.add(key)
                unique_keywords.append(kw.strip())

        metrics = [_metric_for(kw, location, website) for kw in unique_keywords]
        return RankingResult(business_type=business_type, location=location, keywords=metrics)
