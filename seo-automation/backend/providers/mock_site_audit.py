"""Deterministic mock implementation of SiteAuditProvider.

Scores and issues are seeded from a hash of the normalized URL so the same
site always audits the same way (until the mock catalogue changes) — this
mimics the stability a real crawler/PageSpeed integration would have.
"""
import hashlib
import random
import re
from urllib.parse import urlparse

from models.schemas import AuditCategory, AuditIssue, AuditResult
from providers.base import SiteAuditProvider

CATEGORIES = ["Technical SEO", "On-Page SEO", "Performance", "Content", "Links"]

# Each entry: id, title, category, severity, what/why/how_to_fix template strings.
# Affected-page counts are filled in per-run from the seeded RNG.
ISSUE_CATALOG = [
    dict(id="broken-links", title="Broken links", category="Links", severity="critical",
         what="{n} links on the site point to pages that return a 404 or other error response.",
         why="Broken links waste crawl budget, break the flow of link equity between pages, and create a poor experience for visitors who follow them.",
         how_to_fix="Update or remove each broken link, or add a 301 redirect from the missing URL to the closest live equivalent."),
    dict(id="missing-title", title="Missing title tags", category="On-Page SEO", severity="critical",
         what="{n} pages have no <title> tag at all.",
         why="The title tag is the single strongest on-page relevance signal and is what shows as the clickable headline in search results — without one, Google has to guess how to describe the page.",
         how_to_fix="Write a unique, keyword-relevant title (50-60 characters) for every page listed below."),
    dict(id="duplicate-meta", title="Duplicate meta descriptions", category="On-Page SEO", severity="warning",
         what="{n} pages share an identical meta description with at least one other page.",
         why="Duplicate descriptions make it harder for Google to understand each page's distinct purpose and lower click-through rate since search snippets look the same.",
         how_to_fix="Write a unique 150-160 character meta description per page summarizing that page's specific content."),
    dict(id="missing-h1", title="Missing H1", category="On-Page SEO", severity="warning",
         what="{n} pages have no H1 heading.",
         why="The H1 is the clearest on-page signal of what a page is about, both for users skimming the page and for search engines parsing its structure.",
         how_to_fix="Add a single, descriptive H1 near the top of each affected page's content."),
    dict(id="multiple-h1", title="Multiple H1 tags", category="On-Page SEO", severity="opportunity",
         what="{n} pages use more than one H1 heading.",
         why="Multiple H1s dilute the page's topical focus and can make heading hierarchy ambiguous for assistive technology and search crawlers.",
         how_to_fix="Keep one H1 per page and demote the others to H2/H3 based on the content hierarchy."),
    dict(id="large-images", title="Large, unoptimized images", category="Performance", severity="warning",
         what="{n} pages load one or more images heavier than 500KB.",
         why="Oversized images are the most common cause of slow Largest Contentful Paint (LCP), which hurts both user experience and Core Web Vitals-based ranking signals.",
         how_to_fix="Compress and serve images in a modern format (WebP/AVIF), and add explicit width/height attributes to avoid layout shift."),
    dict(id="slow-pages", title="Slow-loading pages", category="Performance", severity="critical",
         what="{n} pages take longer than 3 seconds to reach Largest Contentful Paint on mobile.",
         why="Slow pages increase bounce rate and are directly penalized by Google's page-experience ranking signals.",
         how_to_fix="Reduce render-blocking JS/CSS, enable caching and compression, and lazy-load below-the-fold assets."),
    dict(id="missing-alt", title="Images missing alt text", category="Content", severity="opportunity",
         what="{n} images across the site have no alt attribute.",
         why="Alt text is how screen readers describe images to visually-impaired users and is an accessibility requirement; it also gives search engines extra context for image search.",
         how_to_fix="Add concise, descriptive alt text to every content image (decorative images can use alt=\"\")."),
    dict(id="canonical-problems", title="Canonical tag problems", category="Technical SEO", severity="critical",
         what="{n} pages have a canonical tag pointing to a different, unrelated URL.",
         why="An incorrect canonical tells Google to index a different page instead of this one, which can silently remove pages from search results.",
         how_to_fix="Point each page's canonical tag at itself unless it is intentionally a duplicate of another specific URL."),
    dict(id="indexability", title="Indexability issues", category="Technical SEO", severity="critical",
         what="{n} pages are unintentionally set to noindex or blocked from crawling.",
         why="A page that can't be indexed can never appear in search results, no matter how well optimized its content is.",
         how_to_fix="Remove the noindex meta tag or X-Robots-Tag header from any page that should be discoverable."),
    dict(id="sitemap-issues", title="Sitemap issues", category="Technical SEO", severity="warning",
         what="The XML sitemap references {n} URLs that 404, redirect, or are blocked by robots.txt.",
         why="A sitemap full of dead or blocked URLs wastes crawl budget and can make Search Console treat the whole sitemap as lower quality.",
         how_to_fix="Regenerate the sitemap so it only lists canonical, indexable, 200-status URLs."),
    dict(id="robots-txt", title="robots.txt problems", category="Technical SEO", severity="warning",
         what="robots.txt currently disallows crawling of {n} paths that should be public.",
         why="Overly broad Disallow rules can block search engines from important sections of the site without anyone noticing.",
         how_to_fix="Review each Disallow rule and remove any that unintentionally block indexable content."),
    dict(id="https-issues", title="HTTPS issues", category="Technical SEO", severity="critical",
         what="{n} pages load mixed content (HTTP resources) on an HTTPS page.",
         why="Mixed content triggers browser security warnings and can cause resources to be silently blocked, breaking layout or functionality.",
         how_to_fix="Update all asset URLs (images, scripts, stylesheets) to use https:// or protocol-relative paths."),
]

_PATH_POOL = [
    "/", "/about", "/services", "/contact", "/blog", "/blog/getting-started",
    "/blog/pricing-guide", "/pricing", "/faq", "/locations/downtown",
    "/locations/uptown", "/reviews", "/gallery", "/careers",
]


def _seed_from_url(url: str) -> int:
    normalized = re.sub(r"^https?://", "", url.strip().lower()).rstrip("/")
    return int(hashlib.md5(normalized.encode()).hexdigest(), 16)


class MockSiteAuditProvider(SiteAuditProvider):
    async def run_audit(self, url: str) -> AuditResult:
        rng = random.Random(_seed_from_url(url))

        categories = [
            AuditCategory(name=name, score=rng.randint(58, 96))
            for name in CATEGORIES
        ]
        overall_score = round(sum(c.score for c in categories) / len(categories))

        issues: list[AuditIssue] = []
        for entry in ISSUE_CATALOG:
            # ~65% chance an issue is "found" on this site — the rest pass.
            found = rng.random() < 0.65
            if not found:
                issues.append(AuditIssue(
                    id=entry["id"], title=entry["title"], category=entry["category"],
                    severity="passed",
                    what="No problems of this type were detected.",
                    why="Keeping this clean protects the score in this category.",
                    affected_pages=[], how_to_fix="No action needed.",
                ))
                continue

            n = rng.randint(1, 24)
            affected = rng.sample(_PATH_POOL, k=min(n, len(_PATH_POOL)))
            issues.append(AuditIssue(
                id=entry["id"], title=entry["title"], category=entry["category"],
                severity=entry["severity"],
                what=entry["what"].format(n=n),
                why=entry["why"],
                affected_pages=affected,
                how_to_fix=entry["how_to_fix"],
            ))

        return AuditResult(
            url=url,
            overall_score=overall_score,
            categories=categories,
            issues=issues,
        )
