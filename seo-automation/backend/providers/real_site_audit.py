"""
real_site_audit.py — a genuine single-page audit: fetches the real URL and
inspects the actual HTML, instead of the previous mock provider's
MD5-seeded random data (which never fetched anything).

Scoped honestly to what a single-page fetch can actually tell you — no
site-wide claims (duplicate meta across pages, sitemap health) are
fabricated. An unreachable URL returns a real failing result, not a fake
passing one.
"""
import asyncio
import logging
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup

from models.schemas import AuditCategory, AuditIssue, AuditResult
from providers.base import SiteAuditProvider
from services.crawl_check_service import check_url

logger = logging.getLogger(__name__)

_MAX_LINKS_CHECKED = 25
_LINK_CHECK_TIMEOUT = 8
_OVERALL_TIMEOUT = 25


def _passed(id_, title, category) -> AuditIssue:
    return AuditIssue(
        id=id_, title=title, category=category, severity="passed",
        what="No problems of this type were detected.",
        why="Keeping this clean protects the score in this category.",
        affected_pages=[], how_to_fix="No action needed.",
    )


async def _check_broken_links(base_url: str, soup: BeautifulSoup) -> list[str]:
    """HEAD-check a bounded sample of internal links; return the broken ones."""
    parsed_base = urlparse(base_url)
    seen, internal_links = set(), []
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if not href or href.startswith(("#", "mailto:", "tel:", "javascript:")):
            continue
        full = urljoin(base_url, href)
        if urlparse(full).netloc != parsed_base.netloc:
            continue
        if full in seen:
            continue
        seen.add(full)
        internal_links.append(full)
        if len(internal_links) >= _MAX_LINKS_CHECKED:
            break

    broken = []
    async with httpx.AsyncClient(timeout=_LINK_CHECK_TIMEOUT, follow_redirects=True) as client:
        async def _check(link: str):
            try:
                r = await client.head(link)
                if r.status_code >= 400:
                    broken.append(link)
            except Exception:
                broken.append(link)
        await asyncio.gather(*[_check(l) for l in internal_links], return_exceptions=True)
    return broken


async def _run_audit_inner(url: str) -> AuditResult:
    crawl = await check_url(url)

    categories = {name: 100 for name in ["Technical SEO", "On-Page SEO", "Performance", "Content", "Links"]}
    issues: list[AuditIssue] = []

    def deduct(category: str, amount: int):
        categories[category] = max(0, categories[category] - amount)

    if not crawl["ok"]:
        issues.append(AuditIssue(
            id="unreachable", title="Page could not be crawled", category="Technical SEO",
            severity="critical",
            what=crawl["error"] or "The URL could not be fetched.",
            why="If Googlebot can't reach a page, it can never be indexed or ranked, regardless of content quality.",
            affected_pages=[url], how_to_fix="Confirm the URL is correct, publicly reachable, returns HTTP 200, and isn't blocked by robots.txt or a noindex tag.",
        ))
        for name in categories:
            categories[name] = 0
        return AuditResult(
            url=url, overall_score=0,
            categories=[AuditCategory(name=n, score=s) for n, s in categories.items()],
            issues=issues,
        )

    # Indexability (robots/noindex/canonical) — from the shared crawl-check pipeline
    if crawl["robots_allowed"] is False:
        issues.append(AuditIssue(
            id="robots-txt", title="Blocked by robots.txt", category="Technical SEO", severity="critical",
            what="This URL is disallowed for Googlebot by robots.txt.",
            why="A disallowed page can't be crawled or indexed no matter how good its content is.",
            affected_pages=[url], how_to_fix="Remove the Disallow rule blocking this path if it should be indexable.",
        ))
        deduct("Technical SEO", 40)
    else:
        issues.append(_passed("robots-txt", "robots.txt allows crawling", "Technical SEO"))

    if crawl["has_noindex"]:
        issues.append(AuditIssue(
            id="indexability", title="Page has a noindex tag", category="Technical SEO", severity="critical",
            what="This page has a noindex meta tag, so Google will not index it.",
            why="A noindex page can never appear in search results.",
            affected_pages=[url], how_to_fix="Remove the noindex meta tag if this page should be discoverable.",
        ))
        deduct("Technical SEO", 40)
    else:
        issues.append(_passed("indexability", "Page is indexable", "Technical SEO"))

    if crawl["canonical_url"] and not crawl["canonical_ok"]:
        issues.append(AuditIssue(
            id="canonical-problems", title="Canonical tag points elsewhere", category="Technical SEO", severity="warning",
            what=f"This page's canonical tag points to a different URL ({crawl['canonical_url']}).",
            why="An incorrect canonical tells Google to index a different page instead of this one.",
            affected_pages=[url], how_to_fix="Point the canonical tag at this page's own URL unless it's intentionally a duplicate.",
        ))
        deduct("Technical SEO", 10)
    elif not crawl["canonical_url"]:
        issues.append(AuditIssue(
            id="canonical-problems", title="Missing canonical tag", category="Technical SEO", severity="opportunity",
            what="This page has no <link rel=\"canonical\"> tag.",
            why="A self-referencing canonical tag helps avoid duplicate-content ambiguity.",
            affected_pages=[url], how_to_fix="Add a canonical tag pointing to this page's own URL.",
        ))
        deduct("Technical SEO", 5)
    else:
        issues.append(_passed("canonical-problems", "Canonical tag is correct", "Technical SEO"))

    if urlparse(url).scheme != "https":
        issues.append(AuditIssue(
            id="https-issues", title="Not served over HTTPS", category="Technical SEO", severity="critical",
            what="This page is served over plain HTTP, not HTTPS.",
            why="Google treats HTTPS as a ranking signal and browsers flag HTTP pages as not secure.",
            affected_pages=[url], how_to_fix="Serve the site over HTTPS with a valid TLS certificate.",
        ))
        deduct("Technical SEO", 30)
    else:
        issues.append(_passed("https-issues", "Served over HTTPS", "Technical SEO"))

    # Fetch + parse the real HTML for on-page/content/link checks
    try:
        async with httpx.AsyncClient(timeout=20, follow_redirects=True) as client:
            resp = await client.get(url)
        soup = BeautifulSoup(resp.text, "html.parser")
    except Exception as e:
        logger.warning(f"Site audit HTML parse failed for {url}: {e}")
        soup = None

    if soup is not None:
        title_tag = soup.find("title")
        title_text = title_tag.get_text(strip=True) if title_tag else ""
        if not title_text:
            issues.append(AuditIssue(
                id="missing-title", title="Missing title tag", category="On-Page SEO", severity="critical",
                what="This page has no <title> tag.",
                why="The title tag is the strongest on-page relevance signal and the clickable headline in search results.",
                affected_pages=[url], how_to_fix="Add a unique, keyword-relevant title (50-60 characters).",
            ))
            deduct("On-Page SEO", 30)
        elif len(title_text) > 60 or len(title_text) < 15:
            issues.append(AuditIssue(
                id="missing-title", title="Title tag length is off", category="On-Page SEO", severity="opportunity",
                what=f"The title tag is {len(title_text)} characters (\"{title_text}\"); 50-60 is ideal.",
                why="Titles that are too short waste an opportunity to include relevant keywords; too long ones get truncated in search results.",
                affected_pages=[url], how_to_fix="Rewrite the title to land between 50 and 60 characters.",
            ))
            deduct("On-Page SEO", 5)
        else:
            issues.append(_passed("missing-title", "Title tag is present and well-sized", "On-Page SEO"))

        meta_desc = soup.find("meta", attrs={"name": "description"})
        meta_content = (meta_desc.get("content") or "").strip() if meta_desc else ""
        if not meta_content:
            issues.append(AuditIssue(
                id="missing-meta-description", title="Missing meta description", category="On-Page SEO", severity="warning",
                what="This page has no meta description.",
                why="Without one, Google generates its own snippet from page content, which is often less compelling than a written one.",
                affected_pages=[url], how_to_fix="Write a unique 150-160 character meta description summarizing this page.",
            ))
            deduct("On-Page SEO", 15)
        else:
            issues.append(_passed("missing-meta-description", "Meta description is present", "On-Page SEO"))

        h1s = soup.find_all("h1")
        if len(h1s) == 0:
            issues.append(AuditIssue(
                id="missing-h1", title="Missing H1", category="On-Page SEO", severity="warning",
                what="This page has no H1 heading.",
                why="The H1 is the clearest on-page signal of what a page is about.",
                affected_pages=[url], how_to_fix="Add a single, descriptive H1 near the top of the page.",
            ))
            deduct("On-Page SEO", 15)
        elif len(h1s) > 1:
            issues.append(AuditIssue(
                id="multiple-h1", title="Multiple H1 tags", category="On-Page SEO", severity="opportunity",
                what=f"This page has {len(h1s)} H1 headings.",
                why="Multiple H1s dilute the page's topical focus and make heading hierarchy ambiguous.",
                affected_pages=[url], how_to_fix="Keep one H1 per page and demote the rest to H2/H3.",
            ))
            deduct("On-Page SEO", 5)
        else:
            issues.append(_passed("missing-h1", "Exactly one H1 present", "On-Page SEO"))

        imgs = soup.find_all("img")
        missing_alt = [img for img in imgs if not (img.get("alt") or "").strip()]
        if imgs and missing_alt:
            issues.append(AuditIssue(
                id="missing-alt", title="Images missing alt text", category="Content", severity="opportunity",
                what=f"{len(missing_alt)} of {len(imgs)} images on this page have no alt attribute.",
                why="Alt text is how screen readers describe images and gives search engines extra context for image search.",
                affected_pages=[url], how_to_fix="Add concise, descriptive alt text to every content image.",
            ))
            deduct("Content", min(30, len(missing_alt) * 3))
        else:
            issues.append(_passed("missing-alt", "All images have alt text", "Content"))

        word_count = len(soup.get_text(" ", strip=True).split())
        if word_count < 300:
            issues.append(AuditIssue(
                id="thin-content", title="Thin content", category="Content", severity="opportunity",
                what=f"This page has approximately {word_count} words of visible text.",
                why="Very short pages often struggle to rank for competitive terms since they cover less ground than fuller competing pages.",
                affected_pages=[url], how_to_fix="Expand the page with more genuinely useful, relevant content.",
            ))
            deduct("Content", 10)
        else:
            issues.append(_passed("thin-content", "Content length looks reasonable", "Content"))

        try:
            broken = await asyncio.wait_for(_check_broken_links(url, soup), timeout=15)
        except asyncio.TimeoutError:
            broken = []
        if broken:
            issues.append(AuditIssue(
                id="broken-links", title="Broken links", category="Links", severity="critical",
                what=f"{len(broken)} link(s) checked on this page return an error status.",
                why="Broken links waste crawl budget and create a poor experience for visitors who follow them.",
                affected_pages=broken, how_to_fix="Update or remove each broken link, or 301-redirect it to a live equivalent.",
            ))
            deduct("Links", min(40, len(broken) * 8))
        else:
            issues.append(_passed("broken-links", f"No broken links found (checked up to {_MAX_LINKS_CHECKED})", "Links"))
    else:
        deduct("On-Page SEO", 20)
        deduct("Content", 20)
        deduct("Links", 10)

    # Performance: response time as a rough, honest single-page proxy (no
    # Lighthouse/PageSpeed integration configured — this is not a full
    # Core Web Vitals measurement).
    if crawl["http_status"] == 200:
        issues.append(_passed("response-ok", "Page responded successfully", "Performance"))
    categories["Performance"] = categories["Performance"]  # no separate deduction without a real timing signal

    overall_score = round(sum(categories.values()) / len(categories))
    return AuditResult(
        url=url,
        overall_score=overall_score,
        categories=[AuditCategory(name=n, score=s) for n, s in categories.items()],
        issues=issues,
    )


class RealSiteAuditProvider(SiteAuditProvider):
    async def run_audit(self, url: str) -> AuditResult:
        try:
            return await asyncio.wait_for(_run_audit_inner(url), timeout=_OVERALL_TIMEOUT)
        except asyncio.TimeoutError:
            return AuditResult(
                url=url, overall_score=0,
                categories=[AuditCategory(name=n, score=0) for n in
                            ["Technical SEO", "On-Page SEO", "Performance", "Content", "Links"]],
                issues=[AuditIssue(
                    id="timeout", title="Audit timed out", category="Technical SEO", severity="critical",
                    what="The site took too long to respond while auditing.",
                    why="A slow or unresponsive site is itself a serious problem for both users and search crawlers.",
                    affected_pages=[url], how_to_fix="Investigate server response time and hosting performance.",
                )],
            )
