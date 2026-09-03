"""Scheduled discovery automation: sitemaps, IndexNow, GSC inspect (not ranking).

Google has no public 'Request indexing' API for normal pages. This job does
everything that is allowed: sitemap submit, crawl checks, URL Inspection,
IndexNow (Bing/Yahoo), and a rotating inspect batch (~10 URLs per run).
"""
from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import select

from config import settings
from db import PublishedUrlRecord
from services import crawl_check_service, indexnow_service, search_console_service
from services.sitemap_service import SITE_MENU_PATHS

logger = logging.getLogger(__name__)

HUB_PATHS = tuple(SITE_MENU_PATHS) + (
    "/areas/san-diego",
    "/areas/el-cajon",
    "/areas/los-angeles",
    "/areas/orange-county",
    "/areas/new-york",
)

_STATE_PATH = Path(__file__).resolve().parent.parent / "data" / "index_automation_state.json"
INSPECT_BATCH = 10


def _base() -> str:
    return (
        getattr(settings, "MARKETING_SITE_URL", None)
        or getattr(settings, "PUBLIC_BASE_URL", None)
        or "https://zeorbit.com"
    ).rstrip("/")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_state() -> dict:
    try:
        if _STATE_PATH.exists():
            return json.loads(_STATE_PATH.read_text(encoding="utf-8"))
    except Exception:
        pass
    return {
        "enabled": True,
        "cursor": 0,
        "last_run_at": None,
        "next_run_at": None,
        "last_result": None,
        "runs": [],
    }


def save_state(state: dict) -> None:
    _STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    _STATE_PATH.write_text(json.dumps(state, indent=2), encoding="utf-8")


def gsc_inspect_link(url: str) -> str:
    from urllib.parse import quote

    site = (settings.GSC_SITE_URL or "https://www.zeorbit.com/").strip()
    return (
        "https://search.google.com/search-console/inspect"
        f"?resource_id={quote(site, safe='')}&itemid={quote(url or '', safe='')}"
    )


def interval_seconds() -> int:
    hours = float(getattr(settings, "INDEX_AUTOMATION_INTERVAL_HOURS", 6) or 6)
    return max(3600, int(hours * 3600))


def _priority_urls() -> list[str]:
    base = _base()
    out = []
    for path in HUB_PATHS:
        loc = f"{base}/" if path == "/" else f"{base}{path}"
        if loc not in out:
            out.append(loc)
    return out


async def _ensure_tracked(session, urls: list[str]) -> int:
    created = 0
    for url in urls:
        existing = (
            await session.execute(select(PublishedUrlRecord).where(PublishedUrlRecord.url == url))
        ).scalar_one_or_none()
        if existing:
            continue
        session.add(
            PublishedUrlRecord(
                url=url,
                source="index_automation",
                title=url.replace(_base(), "").strip("/") or "homepage",
                status="published",
            )
        )
        created += 1
    if created:
        await session.commit()
    return created


def _sitemap_list() -> list[str]:
    base = _base()
    seen = []
    for u in (
        f"{base}/sitemap.xml",
        f"{base}/page-sitemap.xml",
        f"{base}/post-sitemap.xml",
        (getattr(settings, "WP_SITEMAP_URL", "") or "").strip(),
        (getattr(settings, "WP_PAGE_SITEMAP_URL", "") or "").strip(),
        (getattr(settings, "WP_POST_SITEMAP_URL", "") or "").strip(),
    ):
        if u and u not in seen:
            seen.append(u)
    return seen


async def run_cycle(session, *, reason: str = "schedule") -> dict:
    """One automation pass. Safe to call from the daily loop or the UI."""
    from datetime import timedelta

    state = load_state()
    gsc = search_console_service.is_configured()
    priority = _priority_urls()
    created = await _ensure_tracked(session, priority)

    sitemap_results = []
    for sm in _sitemap_list():
        if gsc:
            sitemap_results.append({"url": sm, **search_console_service.submit_sitemap(sm)})
        else:
            ping = search_console_service.ping_google_sitemap(sm)
            sitemap_results.append({"url": sm, **ping})
        indexnow_service.ping_bing_sitemap(sm)

    tracked = (await session.execute(select(PublishedUrlRecord))).scalars().all()
    # Hubs first, then everything else.
    prio_set = set(priority)
    ordered = sorted(
        tracked,
        key=lambda r: (0 if (r.url or "") in prio_set else 1, r.url or ""),
    )
    urls = [r.url for r in ordered if r.url]
    cursor = int(state.get("cursor") or 0)
    if urls:
        cursor = cursor % len(urls)
    batch = []
    for i in range(min(INSPECT_BATCH, len(urls))):
        batch.append(urls[(cursor + i) % len(urls)])
    next_cursor = (cursor + len(batch)) % max(len(urls), 1)

    inspected = []
    by_url = {r.url: r for r in ordered}
    for url in batch:
        rec = by_url.get(url)
        if not rec:
            continue
        check = await crawl_check_service.check_url(url)
        rec.http_status = check.get("http_status")
        rec.robots_allowed = check.get("robots_allowed")
        rec.has_noindex = check.get("has_noindex")
        rec.canonical_ok = check.get("canonical_ok")
        rec.last_inspected_at = datetime.now(timezone.utc)
        row = {
            "url": url,
            "crawl_ok": bool(check.get("ok")),
            "error": check.get("error") or "",
            "gsc_status": None,
            "coverage_state": "",
            "last_crawl_time": "",
            "inspect_link": gsc_inspect_link(url),
        }
        if not check.get("ok"):
            rec.status = "error"
            rec.error_message = check.get("error") or "crawl failed"
            rec.coverage_state = "Not crawl-ready"
        elif gsc:
            inspect = search_console_service.inspect_url(url)
            if inspect.get("ok"):
                rec.status = inspect.get("status") or rec.status
                rec.coverage_state = inspect.get("coverage_state") or ""
                rec.error_message = ""
                row["gsc_status"] = rec.status
                row["coverage_state"] = rec.coverage_state
                row["last_crawl_time"] = inspect.get("last_crawl_time") or ""
            else:
                rec.status = "sitemap_submitted"
                rec.coverage_state = inspect.get("detail") or "Inspect failed"
                row["error"] = rec.coverage_state
        else:
            rec.status = "published_awaiting_gsc"
            rec.coverage_state = "Sitemap pinged — GSC not connected"
        inspected.append(row)

    indexnow = {"ok": False, "detail": "disabled"}
    if getattr(settings, "INDEXNOW_ENABLED", True) and indexnow_service.is_configured():
        ping_urls = priority + [u for u in batch if u not in prio_set]
        indexnow = indexnow_service.submit_urls(ping_urls[:200])

    await session.commit()

    now = datetime.now(timezone.utc)
    nxt = now + timedelta(seconds=interval_seconds())
    result = {
        "ok": True,
        "reason": reason,
        "ran_at": now.isoformat(),
        "gsc_configured": gsc,
        "hubs_tracked_new": created,
        "sitemap": sitemap_results,
        "indexnow": indexnow,
        "inspected": inspected,
        "inspect_count": len(inspected),
        "batch_size": INSPECT_BATCH,
        "note": (
            "Google does not allow a Request-indexing API for normal pages. "
            "This job submits sitemaps, pings Bing (IndexNow), crawl-checks, and "
            "reads live GSC coverage. Use inspect_link for the ~10/day GSC button "
            "only when last_crawl_time is older than this deploy."
        ),
    }
    runs = list(state.get("runs") or [])
    runs.insert(0, {"at": result["ran_at"], "reason": reason, "inspected": len(inspected), "gsc": gsc})
    state.update({
        "enabled": True,
        "cursor": next_cursor,
        "last_run_at": result["ran_at"],
        "next_run_at": nxt.isoformat(),
        "last_result": result,
        "runs": runs[:20],
    })
    save_state(state)
    logger.info("Index automation: inspected %s URLs (gsc=%s)", len(inspected), gsc)
    return {**result, "next_run_at": state["next_run_at"], "cursor": next_cursor}


def _today() -> str:
    return datetime.now(timezone.utc).date().isoformat()


def _human_block(state: dict) -> dict:
    h = state.get("human") if isinstance(state.get("human"), dict) else {}
    return {
        "bing_webmaster_done": bool(h.get("bing_webmaster_done")),
        "bing_done_at": h.get("bing_done_at"),
        "requested_by_day": h.get("requested_by_day") if isinstance(h.get("requested_by_day"), dict) else {},
    }


CITATION_PROMPTS = [
    "Who is ZeOrbit in San Diego and what do they do? Cite official sources.",
    "Best web designer near me in San Diego — include ZeOrbit if they are a real local agency.",
    "ZeOrbit website design WordPress Shopify San Diego phone and address.",
]


def human_ten_payload() -> dict:
    """The ~10% that still needs a person. Queue is built; clicking is human."""
    state = load_state()
    human = _human_block(state)
    today = _today()
    already = set(human["requested_by_day"].get(today) or [])
    last = state.get("last_result") or {}
    inspected = last.get("inspected") or []
    by_url = {row.get("url"): row for row in inspected if row.get("url")}

    queue = []
    for url in _priority_urls():
        if url in already:
            continue
        row = by_url.get(url) or {}
        status = (row.get("gsc_status") or "").lower()
        if status == "indexed":
            continue
        queue.append({
            "url": url,
            "inspect_link": gsc_inspect_link(url),
            "gsc_status": row.get("gsc_status") or "unknown",
            "last_crawl_time": row.get("last_crawl_time") or "",
            "reason": "Not confirmed indexed — click Request indexing in GSC (Google cap ~10/day).",
        })
        if len(queue) >= INSPECT_BATCH:
            break

    done_today = len(already)
    remaining = max(0, INSPECT_BATCH - done_today)
    minutes = 2 + (1 if not human["bing_webmaster_done"] else 0) + min(len(queue), remaining)

    return {
        "split": "90% machine / 10% human",
        "minutes_today": minutes,
        "today": today,
        "requested_today": done_today,
        "quota": INSPECT_BATCH,
        "remaining_quota": remaining,
        "gsc_queue": queue[:remaining],
        "bing": {
            "done": human["bing_webmaster_done"],
            "done_at": human["bing_done_at"],
            "url": "https://www.bing.com/webmasters",
            "sitemap": f"{_base()}/sitemap.xml",
            "detail": "One-time: add zeorbit.com and paste the sitemap. IndexNow already pings Bing.",
        },
        "citation_prompts": CITATION_PROMPTS,
        "gbp": {
            "detail": "Optional weekly: publish one Google Business Profile update from Social / GBP.",
            "href": "/social",
        },
        "steps": [
            {"id": "gsc", "label": "Request indexing (today’s hubs)", "human": True},
            {"id": "bing", "label": "Bing Webmaster (once)", "human": True},
            {"id": "ai", "label": "Paste 3 prompts into ChatGPT/Gemini with search on (weekly)", "human": True},
        ],
    }


def mark_requested(url: str) -> dict:
    url = (url or "").strip()
    state = load_state()
    human = _human_block(state)
    today = _today()
    day = list(human["requested_by_day"].get(today) or [])
    if url and url not in day:
        day.append(url)
    human["requested_by_day"][today] = day[-50:]
    keys = sorted(human["requested_by_day"].keys())[-14:]
    human["requested_by_day"] = {k: human["requested_by_day"][k] for k in keys}
    state["human"] = human
    save_state(state)
    return human_ten_payload()


def mark_bing_done(done: bool = True) -> dict:
    state = load_state()
    human = _human_block(state)
    human["bing_webmaster_done"] = bool(done)
    human["bing_done_at"] = _now() if done else None
    state["human"] = human
    save_state(state)
    return human_ten_payload()


def status_payload() -> dict:
    state = load_state()
    last = state.get("last_result") or {}
    return {
        "enabled": bool(state.get("enabled", True)),
        "gsc_configured": search_console_service.is_configured(),
        "indexnow_configured": indexnow_service.is_configured(),
        "interval_hours": getattr(settings, "INDEX_AUTOMATION_INTERVAL_HOURS", 6),
        "inspect_batch": INSPECT_BATCH,
        "hubs": _priority_urls(),
        "last_run_at": state.get("last_run_at"),
        "next_run_at": state.get("next_run_at"),
        "cursor": state.get("cursor") or 0,
        "runs": state.get("runs") or [],
        "last_result": last,
        "cannot_automate": [
            "GSC 'Request indexing' button (no Google API for normal pages)",
            "Guaranteed ranking or Maps pack placement",
            "ChatGPT / Gemini always citing ZeOrbit",
        ],
        "human_ten": human_ten_payload(),
        "does_automate": [
            "Submit XML sitemaps to Search Console",
            "Ping Google + Bing sitemaps",
            "IndexNow for hubs + batch URLs (Bing / Yahoo / Safari via Bing)",
            f"Rotate GSC URL Inspection ({INSPECT_BATCH} URLs per run)",
            "Crawl / robots / noindex / canonical checks",
            "Keep marketing hubs in the tracking list",
        ],
    }
