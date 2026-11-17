"""Publish one SEO page as a live Shopify blog article."""
import httpx
from models.schemas import SEOBlock
from config import settings

_API = "2024-10"


def _store() -> str:
    raw = (settings.SHOPIFY_STORE or "").strip()
    for prefix in ("https://", "http://"):
        if raw.startswith(prefix):
            raw = raw[len(prefix):]
    raw = raw.strip("/")
    return raw


def _html(block: SEOBlock) -> str:
    html = (getattr(block, "content_html", None) or "").strip()
    if html:
        return html
    parts = []
    if (block.intro or "").strip():
        parts.append(f"<p>{block.intro}</p>")
    if (block.content or "").strip():
        parts.append("".join(f"<p>{line}</p>" for line in block.content.split("\n") if line.strip()))
    return "\n".join(parts) or f"<p>{block.title}</p>"


async def publish_article(block: SEOBlock) -> dict:
    store = _store()
    token = (settings.SHOPIFY_ACCESS_TOKEN or "").strip()
    if not store or not token:
        raise RuntimeError("Shopify is not connected. Add SHOPIFY_STORE and SHOPIFY_ACCESS_TOKEN.")
    headers = {"X-Shopify-Access-Token": token, "Content-Type": "application/json"}
    base = f"https://{store}/admin/api/{_API}"
    async with httpx.AsyncClient(timeout=30) as client:
        blog_id = (settings.SHOPIFY_BLOG_ID or "").strip()
        if not blog_id:
            listed = await client.get(f"{base}/blogs.json", headers=headers)
            if listed.status_code >= 400:
                raise RuntimeError("Shopify refused the blog list. Check the store domain and access token.")
            blogs = (listed.json() or {}).get("blogs") or []
            if not blogs:
                raise RuntimeError("This Shopify store has no blog yet.")
            blog_id = str(blogs[0].get("id") or "")
        article = {
            "title": block.title or block.h1 or "Untitled",
            "body_html": _html(block),
            "author": "ZeOrbit",
            "tags": (block.focus_keyword or ""),
            "published": True,
        }
        if (block.meta_description or "").strip():
            article["summary_html"] = f"<p>{block.meta_description}</p>"
        created = await client.post(
            f"{base}/blogs/{blog_id}/articles.json",
            headers=headers,
            json={"article": article},
        )
        if created.status_code >= 400:
            raise RuntimeError("Shopify did not publish the article. Check the blog id and the app permission for content.")
        data = (created.json() or {}).get("article") or {}
        handle = data.get("handle") or ""
        url = f"https://{store}/blogs/{handle}" if handle else ""
        return {"city": block.city or "", "success": True, "post_id": data.get("id"), "post_url": url, "error": None}
