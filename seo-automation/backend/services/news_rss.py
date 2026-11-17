"""Fetch software and design RSS summaries for zeorbit.com/news."""
import re
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from html import unescape
from xml.etree import ElementTree as ET

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db import NewsArticleRecord, NewsFeedRecord

_NS = {
    "content": "http://purl.org/rss/1.0/modules/content/",
    "dc": "http://purl.org/dc/elements/1.1/",
    "media": "http://search.yahoo.com/mrss/",
    "atom": "http://www.w3.org/2005/Atom",
}
# Development work only. General tech, security incidents, and business news stay out.
_IT_DEV = re.compile(
    r"\b("
    r"web development|software development|app development|mobile development|"
    r"front-?end|back-?end|full-?stack|"
    r"javascript|typescript|css|html|react|vue|angular|node\.?js|next\.?js|"
    r"programming|programmer|developers?|coding|codebase|"
    r"api|devops|kubernetes|framework|database|"
    r"wordpress|shopify|web design|ux|ui design|design system|"
    r"accessibility|php|python|ruby|swift|kotlin|flutter|tailwind|"
    r"browser|web platform|component|git|debugging|refactor"
    r")\b",
    re.I,
)
_NOT_DEV = re.compile(
    r"lawsuit|sues\b|hackers?|data breach|\bstolen\b|\baffair\b|\btrump\b|election|celebrity|"
    r"acquires|funding round|layoffs?|black friday|\bdeals\b|developer beta|"
    r"security vulnerabilit|customer support|face unlock",
    re.I,
)


def is_it_development(title: str, summary: str) -> bool:
    blob = f"{title} {summary}"
    if _NOT_DEV.search(blob):
        return False
    return bool(_IT_DEV.search(blob))

DEFAULT_FEEDS = (
    ("Smashing Magazine", "https://www.smashingmagazine.com/feed/", False),
    ("CSS-Tricks", "https://css-tricks.com/feed/", False),
    ("web.dev", "https://web.dev/feed.xml", False),
    ("Chrome for Developers", "https://developer.chrome.com/blog/feed.xml", True),
    ("Stack Overflow Blog", "https://stackoverflow.blog/feed/", False),
    ("TechCrunch", "https://techcrunch.com/feed/", True),
    ("GitHub Blog", "https://github.blog/feed/", True),
    ("Mozilla Hacks", "https://hacks.mozilla.org/feed/", False),
    ("MDN Blog", "https://developer.mozilla.org/en-US/blog/rss.xml", False),
    ("JetBrains", "https://blog.jetbrains.com/feed/", False),
    ("InfoQ", "https://feed.infoq.com/", True),
    ("Microsoft DevBlogs", "https://devblogs.microsoft.com/feed", True),
    ("Shopify Engineering", "https://shopify.engineering/blog.atom", False),
    ("freeCodeCamp", "https://www.freecodecamp.org/news/rss/", True),
    ("Node.js", "https://nodejs.org/en/feed/blog.xml", False),
    ("W3C", "https://www.w3.org/blog/feed/", True),
    ("Spotify Engineering", "https://engineering.atspotify.com/feed", False),
    ("GitLab", "https://about.gitlab.com/atom.xml", True),
    ("Martin Fowler", "https://martinfowler.com/feed.atom", False),
    ("Piccalilli", "https://piccalil.li/feed.xml", False),
    ("Lea Verou", "https://lea.verou.me/feed.xml", False),
    ("Ahmad Shadeed", "https://ishadeed.com/feed.xml", False),
    ("Josh Comeau", "https://www.joshwcomeau.com/rss.xml", False),
    ("Adactio", "https://adactio.com/journal/rss", False),
    ("WebKit", "https://webkit.org/blog/feed/", False),
    ("Google Developers", "https://developers.googleblog.com/feeds/posts/default", True),
    ("Go Blog", "https://go.dev/blog/feed.atom", False),
    ("Rust Blog", "https://blog.rust-lang.org/feed.xml", False),
    ("Kubernetes", "https://kubernetes.io/feed.xml", False),
    ("DEV Community", "https://dev.to/feed", True),
)


def _text(node) -> str:
    if node is None or node.text is None and len(list(node) if node is not None else []) == 0:
        return ""
    return unescape(re.sub(r"\s+", " ", "".join(node.itertext()))).strip()


def _summary(raw: str, limit: int = 280) -> str:
    text = unescape(raw or "")
    text = re.sub(r"<[^>]+>", " ", text)
    text = unescape(re.sub(r"\s+", " ", text)).strip()
    if len(text) <= limit:
        return text
    cut = text[:limit].rsplit(" ", 1)[0].rstrip(".,;:")
    return f"{cut}…"


def _image(node, html: str) -> str:
    for tag in node.findall("media:content", _NS) + node.findall("media:thumbnail", _NS) + node.findall("enclosure"):
        url = (tag.get("url") or "").strip()
        kind = (tag.get("type") or tag.get("medium") or "").lower()
        if url and (not kind or "image" in kind or kind.endswith(("jpg", "jpeg", "png", "webp", "gif"))):
            return url
    match = re.search(r'<img[^>]+src=["\']([^"\']+)', html or "", re.I)
    return match.group(1).strip() if match else ""


def _when(raw: str) -> datetime | None:
    raw = (raw or "").strip()
    if not raw:
        return None
    try:
        parsed = parsedate_to_datetime(raw)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)
    except (TypeError, ValueError, IndexError):
        pass
    try:
        parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)
    except ValueError:
        return None


def _children(root):
    items = root.findall(".//item")
    if items:
        return items, "rss"
    entries = root.findall(".//atom:entry", _NS) or root.findall(".//{http://www.w3.org/2005/Atom}entry")
    return entries, "atom"


def _raw(node) -> str:
    if node is None:
        return ""
    return ET.tostring(node, encoding="unicode")


def _entry(node, kind: str, source: str, filter_software: bool) -> dict | None:
    if kind == "atom":
        title = _text(node.find("atom:title", _NS) or node.find("{http://www.w3.org/2005/Atom}title"))
        link = ""
        for tag in node.findall("atom:link", _NS) + node.findall("{http://www.w3.org/2005/Atom}link"):
            href = (tag.get("href") or "").strip()
            rel = (tag.get("rel") or "alternate").lower()
            if href and rel in {"alternate", ""}:
                link = href
                break
        summary_node = node.find("atom:summary", _NS) or node.find("{http://www.w3.org/2005/Atom}summary")
        content_node = node.find("atom:content", _NS) or node.find("{http://www.w3.org/2005/Atom}content")
        html = _raw(content_node) or _raw(summary_node)
        guid = _text(node.find("atom:id", _NS) or node.find("{http://www.w3.org/2005/Atom}id")) or link
        author = _text(node.find("atom:author/atom:name", _NS))
        published = _when(_text(node.find("atom:published", _NS) or node.find("atom:updated", _NS)))
    else:
        title = _text(node.find("title"))
        link_node = node.find("link")
        link = _text(link_node) or ((link_node.get("href") or "") if link_node is not None else "")
        encoded = node.find("content:encoded", _NS)
        description = node.find("description")
        html = _raw(encoded) or _raw(description)
        guid = _text(node.find("guid")) or link
        author = _text(node.find("dc:creator", _NS)) or _text(node.find("author"))
        published = _when(_text(node.find("pubDate")) or _text(node.find("dc:date", _NS)))
    if not title or not link.startswith("http"):
        return None
    summary = _summary(html)
    if not is_it_development(title, summary):
        return None
    return {
        "guid": guid[:500],
        "url": link[:800],
        "title": title[:400],
        "summary": summary[:600],
        "image_url": _image(node, html).replace("http://", "https://", 1)[:800],
        "author": (author or "")[:160],
        "source_name": source[:160],
        "published_at": published or datetime.now(timezone.utc),
    }


async def ensure_default_feeds(session: AsyncSession) -> None:
    rows = (await session.execute(select(NewsFeedRecord.url))).scalars().all()
    have = {url.rstrip("/") for url in rows}
    added = False
    for name, url, strict in DEFAULT_FEEDS:
        if url.rstrip("/") in have:
            continue
        session.add(NewsFeedRecord(
            name=name,
            url=url,
            source_name=name.split("—")[0].strip(),
            enabled=True,
            filter_software=strict,
            last_status="waiting",
        ))
        added = True
    if added:
        await session.commit()


async def _fetch(url: str) -> str:
    async with httpx.AsyncClient(timeout=20, follow_redirects=True, headers={"User-Agent": "ZeOrbitNews/1.0"}) as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.text.lstrip("\ufeff")


async def _og_image(client: httpx.AsyncClient, url: str) -> str:
    try:
        response = await client.get(url, timeout=8)
        if response.status_code >= 400:
            return ""
        head = response.text[:30000]
        match = re.search(
            r'<meta[^>]+(?:property|name)=["\']og:image(?::secure_url)?["\'][^>]+content=["\']([^"\']+)',
            head,
            re.I,
        ) or re.search(
            r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+(?:property|name)=["\']og:image',
            head,
            re.I,
        )
        image = (match.group(1).strip() if match else "")
        if image.startswith("//"):
            image = f"https:{image}"
        return image.replace("http://", "https://", 1)[:800] if image.startswith("http") else ""
    except Exception:
        return ""


async def sync_feed(session: AsyncSession, feed: NewsFeedRecord) -> dict:
    added = 0
    feed_id = feed.id
    feed_name = feed.name
    try:
        async with httpx.AsyncClient(timeout=20, follow_redirects=True, headers={"User-Agent": "ZeOrbitNews/1.0"}) as client:
            response = await client.get(feed.url)
            response.raise_for_status()
            raw = response.text.lstrip("\ufeff")
            root = _parse(raw)
            nodes, kind = _children(root)
            pending = []
            for node in nodes[:40]:
                item = _entry(node, kind, feed.source_name or feed.name, bool(feed.filter_software))
                if not item:
                    continue
                found = (await session.execute(
                    select(NewsArticleRecord.id).where(
                        (NewsArticleRecord.url == item["url"]) | (NewsArticleRecord.guid == item["guid"])
                    ).limit(1)
                )).scalar_one_or_none()
                if found:
                    continue
                pending.append(item)
            looked = 0
            for item in pending:
                if not item["image_url"] and looked < 8:
                    item["image_url"] = await _og_image(client, item["url"])
                    looked += 1
                session.add(NewsArticleRecord(feed_id=feed.id, hidden=False, **item))
                added += 1
        feed.last_status = "ok"
        feed.last_error = ""
        feed.last_added = added
        feed.last_synced_at = datetime.now(timezone.utc)
        await session.commit()
        return {"feed": feed_name, "added": added, "ok": True}
    except Exception as exc:
        await session.rollback()
        row = await session.get(NewsFeedRecord, feed_id)
        if row:
            row.last_status = "error"
            row.last_error = str(exc)[:400]
            row.last_added = 0
            row.last_synced_at = datetime.now(timezone.utc)
            await session.commit()
        return {"feed": feed_name, "added": 0, "ok": False, "error": str(exc)[:400]}


async def fill_missing_images(session: AsyncSession, limit: int = 12) -> int:
    rows = (await session.execute(
        select(NewsArticleRecord)
        .where(NewsArticleRecord.image_url == "", NewsArticleRecord.hidden == False)
        .order_by(NewsArticleRecord.published_at.desc())
        .limit(limit)
    )).scalars().all()
    if not rows:
        return 0
    filled = 0
    async with httpx.AsyncClient(timeout=8, follow_redirects=True, headers={"User-Agent": "ZeOrbitNews/1.0"}) as client:
        for row in rows:
            image = await _og_image(client, row.url)
            if image:
                row.image_url = image
                filled += 1
            else:
                row.image_url = " "
    await session.commit()
    return filled


async def hide_off_topic(session: AsyncSession) -> int:
    rows = (await session.execute(select(NewsArticleRecord).where(NewsArticleRecord.hidden == False))).scalars().all()
    hidden = 0
    for row in rows:
        if is_it_development(row.title or "", row.summary or ""):
            continue
        row.hidden = True
        hidden += 1
    if hidden:
        await session.commit()
    return hidden


async def sync_enabled(session: AsyncSession) -> list[dict]:
    await ensure_default_feeds(session)
    feeds = (await session.execute(select(NewsFeedRecord).where(NewsFeedRecord.enabled == True))).scalars().all()
    results = []
    for feed in feeds:
        results.append(await sync_feed(session, feed))
    await hide_off_topic(session)
    await fill_missing_images(session)
    return results


def _parse(raw: str):
    try:
        return ET.fromstring(raw)
    except ET.ParseError:
        cleaned = re.sub(r"&(?!amp;|lt;|gt;|quot;|apos;|#)", "&amp;", raw)
        return ET.fromstring(cleaned)
