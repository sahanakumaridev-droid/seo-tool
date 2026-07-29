"""Deterministic mock implementation of KeywordDataProvider.

Volume/difficulty/CPC/intent/trend are seeded from a hash of the keyword +
location, so repeated searches for the same term are stable. Related terms
reuse the existing Datamuse lookup (services/keyword_service.py) for
realistic-sounding related words, then layer in the mock metrics.
"""
import hashlib
import random

from models.schemas import KeywordMetric, KeywordResearchResult
from providers.base import KeywordDataProvider
from services.keyword_service import fetch_datamuse_words

INTENTS = ["Informational", "Commercial", "Transactional", "Navigational"]
SERP_FEATURE_POOL = [
    "Featured Snippet", "People Also Ask", "Local Pack", "Site Links",
    "Image Pack", "Video Carousel", "Top Stories", "Reviews",
]
MODIFIERS = [
    "near me", "best", "cost", "reviews", "vs", "for beginners",
    "services", "company", "prices", "how to choose",
]

TRANSACTIONAL_HINTS = ("buy", "hire", "near me", "cost", "price", "quote", "book")
COMMERCIAL_HINTS = ("best", "top", "vs", "review", "company", "service")
NAVIGATIONAL_HINTS = ("login", "sign in", "website", "app", "contact")


def _seed(text: str) -> int:
    return int(hashlib.md5(text.strip().lower().encode()).hexdigest(), 16)


def _infer_intent(keyword: str, rng: random.Random) -> str:
    kw = keyword.lower()
    if any(h in kw for h in NAVIGATIONAL_HINTS):
        return "Navigational"
    if any(h in kw for h in TRANSACTIONAL_HINTS):
        return "Transactional"
    if any(h in kw for h in COMMERCIAL_HINTS):
        return "Commercial"
    if kw.startswith(("how", "what", "why", "when", "who", "is ", "are ")):
        return "Informational"
    return rng.choice(INTENTS)


def _build_metric(keyword: str, location: str, base_volume: int | None = None) -> KeywordMetric:
    rng = random.Random(_seed(f"{keyword}|{location}"))
    intent = _infer_intent(keyword, rng)

    if base_volume is None:
        volume = rng.choice([
            rng.randint(20, 300), rng.randint(300, 2000),
            rng.randint(2000, 12000), rng.randint(12000, 40000),
        ])
    else:
        # Related keywords scale down from the primary term's volume.
        volume = max(10, int(base_volume * rng.uniform(0.05, 0.6)))

    difficulty = rng.randint(8, 92)
    cpc_base = 0.8 + (difficulty / 100) * 12
    intent_multiplier = {"Transactional": 1.8, "Commercial": 1.3, "Informational": 0.4, "Navigational": 0.5}[intent]
    cpc = round(cpc_base * intent_multiplier * rng.uniform(0.8, 1.3), 2)

    trend_pct = rng.randint(-18, 34)
    trend = f"{'+' if trend_pct >= 0 else ''}{trend_pct}%"

    n_features = rng.randint(0, 3)
    serp_features = rng.sample(SERP_FEATURE_POOL, k=n_features)

    return KeywordMetric(
        keyword=keyword, volume=volume, difficulty=difficulty, cpc=cpc,
        intent=intent, trend=trend, serp_features=serp_features,
    )


class MockKeywordDataProvider(KeywordDataProvider):
    async def research(self, keyword: str, location: str = "US") -> KeywordResearchResult:
        keyword = keyword.strip()
        primary = _build_metric(keyword, location)

        related_terms: list[str] = []
        datamuse_words = await fetch_datamuse_words(keyword, max_results=8)
        related_terms += [f"{w} {keyword}" for w in datamuse_words[:4]]
        related_terms += [f"{keyword} {mod}" for mod in MODIFIERS]

        seen = {keyword.lower()}
        related: list[KeywordMetric] = []
        for term in related_terms:
            key = term.lower().strip()
            if key in seen:
                continue
            seen.add(key)
            related.append(_build_metric(term, location, base_volume=primary.volume))
            if len(related) >= 12:
                break

        return KeywordResearchResult(
            location=location, language="English", primary=primary, related=related,
        )
