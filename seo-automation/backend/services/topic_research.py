"""Public-web facts for a search query — Wikipedia + DuckDuckGo.

Used so blog generation stays on-topic with real data (Typefully-style),
instead of a city tourism page.
"""
from __future__ import annotations

import asyncio
from typing import Any
from urllib.parse import quote, quote_plus

import httpx
from bs4 import BeautifulSoup

_UA = {
    "User-Agent": "Mozilla/5.0 (compatible; ZeOrbitSEO/2.1; +https://zeorbit.com)",
    "Accept": "application/json, text/html;q=0.9,*/*;q=0.8",
}


_research_cache: dict[str, dict[str, Any]] = {}
_research_inflight: dict[str, asyncio.Task] = {}


async def research_topic(query: str) -> dict[str, Any]:
    q = (query or "").strip()
    key = q.lower()
    if key in _research_cache:
        return _research_cache[key]
    task = _research_inflight.get(key)
    if task is None:
        task = asyncio.create_task(_research_topic_uncached(q))
        _research_inflight[key] = task
    try:
        return await task
    finally:
        _research_inflight.pop(key, None)


async def _research_topic_uncached(q: str) -> dict[str, Any]:
    key = q.lower()
    out = {"query": q, "extract": "", "title": "", "related": [], "sources": []}
    if len(q) < 3:
        return out
    wiki, ddg = {}, {}
    async with httpx.AsyncClient(timeout=4.0, headers=_UA, follow_redirects=True) as client:
        wiki_task = asyncio.create_task(_wikipedia(client, q))
        ddg_task = asyncio.create_task(_duckduckgo(client, q))
        done = await asyncio.gather(wiki_task, ddg_task, return_exceptions=True)
        if not isinstance(done[0], Exception):
            wiki = done[0] or {}
        else:
            print(f"[Research] wikipedia {q[:60]!r}: {done[0]}")
        if not isinstance(done[1], Exception):
            ddg = done[1] or {}
        else:
            print(f"[Research] ddg {q[:60]!r}: {done[1]}")
    extract = (wiki.get("extract") or ddg.get("extract") or "").strip()
    title = wiki.get("title") or ddg.get("title") or q
    related = (wiki.get("related") or []) + (ddg.get("related") or [])
    seen = set()
    uniq = []
    for r in related:
        t = (r or "").strip()
        k = t.lower()
        if t and k not in seen:
            seen.add(k)
            uniq.append(t[:220])
        if len(uniq) >= 6:
            break
    sources = [s for s in (wiki.get("sources") or []) + (ddg.get("sources") or []) if s]
    out.update(extract=extract[:900], title=title, related=uniq, sources=sources[:6])
    if key:
        _research_cache[key] = out
        if len(_research_cache) > 400:
            _research_cache.pop(next(iter(_research_cache)))
    return out


def research_prompt_block(research: dict | None) -> str:
    if not research:
        return ""
    extract = (research.get("extract") or "").strip()
    related = research.get("related") or []
    sources = research.get("sources") or []
    if not extract and not related and not sources:
        return ""
    lines = [
        "RESEARCH NOTES (public sources gathered before writing):",
        "Use only facts that appear below. Do not invent statistics, prices, dates, or quotes.",
        "If a fact is not in these notes, leave it out.",
    ]
    if extract:
        lines.append(extract)
    for r in related[:5]:
        lines.append(f"- {r}")
    if sources:
        lines.append("SOURCES (cite these in a short References list at the end of content, and nowhere else):")
        for s in sources[:6]:
            if isinstance(s, dict):
                title = s.get("title") or s.get("name") or "Source"
                url = s.get("url") or ""
                lines.append(f"- {title} {url}".strip())
            else:
                lines.append(f"- {s}")
    lines.append("Stay on the editor's search query. Do not write a city tourism guide.")
    return "\n".join(lines)


async def _wikipedia(client: httpx.AsyncClient, query: str) -> dict:
    r = await client.get(
        "https://en.wikipedia.org/w/api.php",
        params={
            "action": "query",
            "list": "search",
            "srsearch": query,
            "srlimit": 1,
            "utf8": 1,
            "format": "json",
        },
    )
    if r.status_code != 200:
        return {}
    hits = ((r.json() or {}).get("query") or {}).get("search") or []
    if not hits:
        return {}
    title = hits[0].get("title") or ""
    snippet = (hits[0].get("snippet") or "")
    snippet = snippet.replace('<span class="searchmatch">', "").replace("</span>", "")
    return {
        "title": title,
        "extract": snippet,
        "related": [],
        "sources": [],
    }


async def _duckduckgo(client: httpx.AsyncClient, query: str) -> dict:
    r = await client.get(
        "https://api.duckduckgo.com/",
        params={"q": query, "format": "json", "no_html": 1, "skip_disambig": 1},
    )
    if r.status_code != 200:
        return {}
    try:
        data = r.json() or {}
    except Exception:
        return {}
    extract = (data.get("AbstractText") or data.get("Abstract") or "").strip()
    related = []
    for item in data.get("RelatedTopics") or []:
        if isinstance(item, dict) and item.get("Text"):
            related.append(item["Text"])
        elif isinstance(item, dict):
            for sub in item.get("Topics") or []:
                if isinstance(sub, dict) and sub.get("Text"):
                    related.append(sub["Text"])
    url = data.get("AbstractURL") or ""
    return {
        "title": data.get("Heading") or "",
        "extract": extract,
        "related": related[:6],
        "sources": [url] if url else [],
    }


async def _ddg_html(client: httpx.AsyncClient, query: str) -> dict:
    r = await client.get(f"https://html.duckduckgo.com/html/?q={quote_plus(query)}")
    if r.status_code != 200 or not r.text:
        return {}
    soup = BeautifulSoup(r.text, "html.parser")
    related = []
    extract = ""
    sources = []
    for res in soup.select(".result")[:6]:
        title = (res.select_one("a.result__a") or res.select_one("a")).get_text(" ", strip=True) if res.select_one("a") else ""
        snip = ""
        sn_el = res.select_one(".result__snippet") or res.select_one(".result__body")
        if sn_el:
            snip = sn_el.get_text(" ", strip=True)
        if title and snip:
            related.append(f"{title}: {snip}"[:220])
            if not extract:
                extract = snip[:500]
        href = ""
        a = res.select_one("a.result__a")
        if a and a.get("href"):
            href = a["href"]
        if href:
            sources.append(href.split("#")[0][:200])
    return {"extract": extract, "related": related, "sources": sources, "title": ""}
