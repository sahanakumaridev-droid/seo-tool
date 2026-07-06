"""
internal_linking_service.py
Inserts contextually relevant internal links into article body content using the
page inventory discovered by website_analysis_service.

Strategy:
- Score each site page against the article text by anchor-phrase overlap.
- Guarantee coverage of the four important link types (service, blog, location, contact)
  when such pages exist in the inventory.
- Cap total links so the content stays natural.
"""
import re
from typing import List, Set
from models.schemas import SitePage

# Order in which we try to guarantee one link per important type.
_PRIORITY_TYPES = ["service", "blog", "location", "contact"]


def _anchor_for(page: SitePage) -> str:
    """Pick a readable anchor phrase for a page."""
    if page.title and 2 <= len(page.title) <= 60:
        return page.title.strip()
    # Derive from the URL slug.
    slug = re.sub(r"[-_/]+", " ", page.url.rstrip("/").split("/")[-1]).strip()
    return slug.title() if slug else "learn more"


def _find_phrase_span(text: str, phrase: str):
    """Case-insensitive whole-phrase match that isn't already inside an anchor tag."""
    if not phrase or len(phrase) < 3:
        return None
    pattern = re.compile(r"(?<![\w>])(" + re.escape(phrase) + r")(?![\w<])", re.IGNORECASE)
    for m in pattern.finditer(text):
        # Skip if this occurrence is already inside an <a ...>...</a>.
        preceding = text[:m.start()]
        if preceding.rfind("<a ") > preceding.rfind("</a>"):
            continue
        return m
    return None


def insert_internal_links(
    body: str,
    page_inventory: List[SitePage],
    max_links: int = 5,
) -> str:
    """Return body with up to max_links contextual internal links inserted."""
    if not body or not page_inventory:
        return body

    used_urls: Set[str] = set()
    links_added = 0

    def try_link_page(page: SitePage) -> bool:
        nonlocal body, links_added
        if page.url in used_urls or links_added >= max_links:
            return False
        anchor = _anchor_for(page)
        m = _find_phrase_span(body, anchor)
        matched_text = None
        if m:
            matched_text = m.group(1)
        else:
            # Fall back to the page_type keyword so priority types still link.
            for kw in (page.page_type, "contact us", "our services", "learn more"):
                m = _find_phrase_span(body, kw)
                if m:
                    matched_text = m.group(1)
                    break
        if not m or not matched_text:
            return False
        replacement = f'<a href="{page.url}">{matched_text}</a>'
        body = body[:m.start()] + replacement + body[m.end():]
        used_urls.add(page.url)
        links_added += 1
        return True

    # 1) Guarantee one link per priority type when available.
    for ptype in _PRIORITY_TYPES:
        candidates = [p for p in page_inventory if p.page_type == ptype]
        for page in candidates:
            if try_link_page(page):
                break

    # 2) Fill remaining slots with any other pages (blog/service preferred).
    remaining = sorted(
        [p for p in page_inventory if p.url not in used_urls and p.page_type != "home"],
        key=lambda p: 0 if p.page_type in ("service", "blog") else 1,
    )
    for page in remaining:
        if links_added >= max_links:
            break
        try_link_page(page)

    return body
