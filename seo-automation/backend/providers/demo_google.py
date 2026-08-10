"""
demo_google.py — optional local simulation for Google Indexing, GBP, and Ads.

Production order of preference (free first):
  1. Live free Google APIs when credentials are configured
  2. Free crawl checks / free LLM (Groq/Gemini) when Google OAuth isn't set
  3. DEMO_MODE simulation only when explicitly enabled AND live APIs aren't available

Never pretend a demo action was a live Google publish when credentials exist.
"""
from __future__ import annotations

import hashlib
import uuid
from datetime import datetime, timezone, timedelta
from typing import List

from config import settings


def demo_enabled() -> bool:
    return bool(settings.DEMO_MODE)


def use_demo_fallback(live_configured: bool) -> bool:
    """Demo only when DEMO_MODE is on and the real free/live API isn't ready."""
    return demo_enabled() and not live_configured


DEMO_INDEX_URLS = [
    {
        "url": "https://demo.zeorbit.com/web-design-san-diego",
        "title": "Web Design in San Diego, CA",
        "status": "indexed",
        "http_status": 200,
        "coverage_state": "Submitted and indexed",
    },
    {
        "url": "https://demo.zeorbit.com/web-design-la-jolla",
        "title": "Web Design in La Jolla, CA",
        "status": "discovered",
        "http_status": 200,
        "coverage_state": "Discovered – currently not indexed",
    },
    {
        "url": "https://demo.zeorbit.com/web-design-coronado",
        "title": "Web Design in Coronado, CA",
        "status": "sitemap_added",
        "http_status": 200,
        "coverage_state": "URL is known to Google",
    },
    {
        "url": "https://demo.zeorbit.com/seo-services-chula-vista",
        "title": "SEO Services in Chula Vista, CA",
        "status": "published",
        "http_status": 200,
        "coverage_state": "",
    },
    {
        "url": "https://demo.zeorbit.com/local-seo-carlsbad",
        "title": "Local SEO in Carlsbad, CA",
        "status": "not_indexed",
        "http_status": 200,
        "coverage_state": "Crawled – currently not indexed",
    },
]


def demo_index_row(seed: dict, idx: int) -> dict:
    now = datetime.now(timezone.utc)
    return {
        "id": -(idx + 1),
        "url": seed["url"],
        "source": "demo",
        "post_id": f"demo-{idx + 1}",
        "title": seed["title"],
        "status": seed["status"],
        "http_status": seed["http_status"],
        "robots_allowed": True,
        "has_noindex": False,
        "canonical_ok": True,
        "coverage_state": seed.get("coverage_state", ""),
        "error_message": "",
        "sitemap_submitted_at": (now - timedelta(days=3 - (idx % 3))).isoformat(),
        "last_inspected_at": (now - timedelta(hours=2 + idx)).isoformat(),
        "created_at": (now - timedelta(days=5 + idx)).isoformat(),
        "updated_at": now.isoformat(),
        "demo": True,
    }


def build_demo_index_urls() -> List[dict]:
    return [demo_index_row(s, i) for i, s in enumerate(DEMO_INDEX_URLS)]


def demo_gbp_post_name(message: str) -> str:
    digest = hashlib.sha1(message.encode("utf-8")).hexdigest()[:10]
    return f"accounts/demo/locations/demo/localPosts/demo-{digest}"


def demo_ads_campaign(campaign_name: str) -> dict:
    cid = str(abs(hash(campaign_name + uuid.uuid4().hex[:6])) % 10_000_000_000)
    return {
        "success": True,
        "campaign_id": cid,
        "campaign_resource_name": f"customers/0000000000/campaigns/{cid}",
        "ad_group_resource_name": f"customers/0000000000/adGroups/{cid}01",
        "manage_url": f"https://ads.google.com/aw/campaigns?campaignId={cid}",
        "error": None,
        "demo": True,
    }


def free_gbp_message(business_name: str = "", city: str = "", service: str = "") -> str:
    biz = (business_name or "Our team").strip()
    place = (city or "your area").strip()
    svc = (service or "services").strip()
    return (
        f"{biz} is helping customers across {place} with reliable {svc.lower()}. "
        f"Book a free consultation this week — limited slots available. "
        f"Call or message us to get started!"
    )[:1500]
