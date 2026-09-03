from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from db import get_session, PageRecord, PublishedUrlRecord
from services.content_service import generate_seo_block
from services.slug_utils import article_slug
from models.schemas import SEOBlock
from config import settings
from datetime import datetime, timezone
from typing import List, Optional
from pydantic import BaseModel
from urllib.parse import urlparse
import re

router = APIRouter()

LIVE_SITE = "https://zeorbit.com"


def slugify(text: str) -> str:
    return re.sub(r'[^a-z0-9-]+', '-', text.lower()).strip('-')


def _block_slug(block: SEOBlock) -> str:
    if (block.slug or "").strip():
        return block.slug.strip()
    kws = []
    if getattr(block, "focus_keyword", None):
        kws.append(block.focus_keyword)
    if block.keywords:
        if block.keywords.primary:
            kws.append(block.keywords.primary)
        kws.extend(block.keywords.secondary or [])
    return article_slug(kws, block.city or "", block.business_type or "") or slugify(
        f"{block.business_type}-{block.city}-{block.state}"
    )


def _is_tool_host(url_or_host: str) -> bool:
    h = (url_or_host or "").lower()
    return "nip.io" in h or "://seo." in h


def _reader_base(request: Optional[Request] = None) -> str:
    """Live ZeOrbit site — published blogs must open here, not on the SEO host."""
    marketing = (getattr(settings, "MARKETING_SITE_URL", None) or "").strip().rstrip("/")
    if marketing:
        return marketing
    if settings.PUBLIC_BASE_URL:
        base = settings.PUBLIC_BASE_URL.rstrip("/")
        if not _is_tool_host(base):
            return base
    if request is not None:
        origin = str(request.base_url).rstrip("/")
        if origin and not _is_tool_host(origin) and "127.0.0.1" not in origin and "localhost" not in origin:
            return origin
    return LIVE_SITE


def _public_base(request: Request) -> str:
    """Reader-facing base for /p/{slug} links (always the live website)."""
    return _reader_base(request)


def _plain_excerpt(block: dict, title: str = "") -> str:
    dummy = {"published live seo article.", "published live seo article"}
    for key in ("meta_description", "intro", "content"):
        raw = (block.get(key) or "").strip()
        if not raw:
            continue
        raw = re.sub(r"^#+\s*", "", raw)
        raw = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", raw)
        raw = re.sub(r"<[^>]+>", " ", raw)
        raw = re.sub(r"\s+", " ", raw).strip()
        if raw.lower() in dummy:
            continue
        if len(raw) > 180:
            raw = raw[:177].rstrip() + "…"
        if raw:
            return raw
    t = (title or "").strip()
    if t and t.lower() not in dummy:
        return t if t.endswith(".") else f"{t}."
    return ""


def _is_blog_block(block: dict) -> bool:
    return (block.get("content_type") or "service").lower() in ("blog", "post")


def _rewrite_reader_url(url: str, slug: str = "") -> str:
    """Map SEO-tool / nip.io URLs onto the live website."""
    base = _reader_base()
    if slug:
        return f"{base}/{slug.lstrip('/')}"
    raw = (url or "").strip()
    if not raw:
        return f"{base}/blog"
    if raw.startswith("/p/"):
        return f"{base}/{raw[3:].split('?')[0]}"
    try:
        parsed = urlparse(raw if "://" in raw else f"https://{raw}")
    except Exception:
        return f"{base}/blog"
    path = parsed.path or "/"
    host = (parsed.hostname or "").lower()
    if path.startswith("/p/"):
        return f"{base}/{path[3:].rstrip('/')}"
    if "nip.io" in host or host.startswith("seo."):
        return f"{base}/blog"
    return raw


def _ads_ready_url(url: str) -> bool:
    """Google Ads requires a public domain with a real TLD (not localhost/IP)."""
    try:
        from urllib.parse import urlparse
        import re
        host = (urlparse(url if "://" in url else f"https://{url}").hostname or "").strip()
        if not host or host in {"localhost"} or host.replace(".", "").isdigit():
            return False
        if re.match(r"^(127\.|10\.|192\.168\.|0\.)", host):
            return False
        return bool(re.match(r"^[a-z0-9-]+(\.[a-z0-9-]+)*\.[a-z]{2,}$", host, re.I))
    except Exception:
        return False


@router.get("/landing-pages", response_model=dict)
async def list_landing_pages_for_ads(
    request: Request,
    skip: int = 0,
    limit: int = 50,
    session: AsyncSession = Depends(get_session),
):
    """
    Published SEO landing pages ready to use as Google Ads final URLs.
    Prefer WordPress live URLs and /p/{slug} pages with a public PUBLIC_BASE_URL.
    """
    base = _public_base(request)
    limit = max(1, min(limit, 100))
    skip = max(0, skip)

    pages = []
    page_result = await session.execute(
        select(PageRecord).order_by(PageRecord.created_at.desc()).limit(200)
    )
    for r in page_result.scalars().all():
        block = r.seo_block if isinstance(r.seo_block, dict) else {}
        title = (block.get("title") or block.get("h1") or r.business_type or "Untitled").strip()
        public_url = f"{base}/{r.slug}"
        keywords = []
        kw = block.get("keywords") or {}
        if isinstance(kw, dict):
            if kw.get("primary"):
                keywords.append(kw["primary"])
            keywords.extend([x for x in (kw.get("secondary") or []) if x][:6])
        pages.append({
            "id": f"page-{r.id}",
            "source": "seo",
            "title": title,
            "slug": r.slug,
            "public_url": public_url,
            "business_type": r.business_type or block.get("business_type") or "",
            "city": r.city or "",
            "state": r.state or "",
            "keywords": keywords,
            "ads_ready": _ads_ready_url(public_url),
            "published_at": (r.updated_at or r.created_at).isoformat() if (r.updated_at or r.created_at) else None,
        })

    try:
        wp_result = await session.execute(
            select(PublishedUrlRecord)
            .where(PublishedUrlRecord.status != "error")
            .order_by(PublishedUrlRecord.created_at.desc())
            .limit(100)
        )
        for u in wp_result.scalars().all():
            if not u.url:
                continue
            pages.append({
                "id": f"wp-{u.id}",
                "source": "wordpress",
                "title": (u.title or u.url).strip(),
                "slug": "",
                "public_url": u.url,
                "business_type": "",
                "city": "",
                "state": "",
                "keywords": [],
                "ads_ready": _ads_ready_url(u.url),
                "published_at": u.created_at.isoformat() if u.created_at else None,
            })
    except Exception:
        pass

    ready = [p for p in pages if p.get("ads_ready")]
    not_ready = [p for p in pages if not p.get("ads_ready")]
    ready.sort(key=lambda p: p.get("published_at") or "", reverse=True)
    not_ready.sort(key=lambda p: p.get("published_at") or "", reverse=True)
    ordered = ready + not_ready
    total = len(ordered)
    return {
        "pages": ordered[skip: skip + limit],
        "total": total,
        "public_base_url": base,
        "ads_ready_count": len(ready),
    }


@router.post("/publish-web", response_model=dict)
async def publish_to_web(
    block: SEOBlock,
    request: Request,
    session: AsyncSession = Depends(get_session),
    force: bool = False,
):
    """Save an already-generated page and expose it at a public /{slug} URL.

    Refuses publish when master quality gates fail unless force=true.
    """
    from services.publish_pipeline import track_public_publish, maybe_auto_create_ads
    from services.zeorbit_local_seo import MIN_PUBLISH_SCORE, MIN_KEYWORD_USE_SCORE, scores_meet_floor

    from services.zeorbit_local_seo import apply_zip_faq_only
    apply_zip_faq_only(block, getattr(block, "city", "") or "", getattr(block, "state", "") or "", getattr(block, "zip", "") or "")

    q = float(getattr(block, "quality_score", None) or getattr(block, "readability_score", None) or 0)
    kw = float(getattr(block, "keyword_density", None) or 0)
    if not force and getattr(block, "content_type", "service") == "service":
        from services.zeorbit_local_seo import copy_has_zip, digits_zip
        faq_blob = ""
        if block.faqs:
            for faq in block.faqs:
                faq_blob += f" {getattr(faq, 'question', '') or ''} {getattr(faq, 'answer', '') or ''}"
        if not digits_zip(getattr(block, "zip", "") or "") or not copy_has_zip(faq_blob, getattr(block, "zip", "") or ""):
            raise HTTPException(
                status_code=400,
                detail="ZIP is mandatory in FAQ answers (as a hyperlink). Do not put the ZIP in the body. Generate again or add it to an FAQ before publish.",
            )
        if block.publishable is False or not scores_meet_floor(q, kw):
            raise HTTPException(
                status_code=400,
                detail={
                    "message": (
                        f"Scores must both be {int(MIN_PUBLISH_SCORE)}%+ before publish "
                        f"(Quality {round(q)}%, Keyword use {round(kw)}%). "
                        "Correct the copy or use AI fix on the preview."
                    ),
                    "quality_score": q,
                    "keyword_density": kw,
                    "min_score": MIN_PUBLISH_SCORE,
                    "min_keyword_use": MIN_KEYWORD_USE_SCORE,
                    "quality_breakdown": block.quality_breakdown,
                },
            )

    # Canonical image sync: featured/footer from the same in_content set.
    imgs = block.in_content_images or []
    if imgs:
        from services.image_service import assign_canonical_images
        feat, foot, cleaned = assign_canonical_images(list(imgs))
        block.in_content_images = cleaned
        if feat:
            block.featured_image_url = feat
        if foot:
            block.footer_image_url = foot

    slug = _block_slug(block)
    block.slug = slug

    result = await session.execute(select(PageRecord).where(PageRecord.slug == slug))
    existing = result.scalar_one_or_none()
    if existing:
        existing.seo_block = block.model_dump()
        existing.updated_at = datetime.now(timezone.utc)
    else:
        session.add(PageRecord(
            business_type=block.business_type,
            base_location=f"{block.city}, {block.state}",
            city=block.city,
            state=block.state or "",
            slug=slug,
            seo_block=block.model_dump(),
        ))
    await session.commit()

    public_url = f"{_public_base(request)}/{slug}"
    indexing = await track_public_publish(url=public_url, block=block, session=session)
    ads = await maybe_auto_create_ads(public_url=public_url, block=block)
    try:
        from services.sitemap_service import persist_live_sitemaps
        await persist_live_sitemaps(session, site_base=_public_base(request))
    except Exception:
        pass

    return {
        "slug": slug,
        "public_url": public_url,
        "published": True,
        "indexing": indexing,
        "ads": ads,
        "quality_score": block.quality_score,
        "publishable": block.publishable,
        "automation": {
            "ads_auto_create": bool(settings.GOOGLE_ADS_AUTO_CREATE_ON_PUBLISH),
            "ads_auto_enable": bool(settings.GOOGLE_ADS_AUTO_ENABLE),
        },
    }


@router.post("/publish-web/bulk", response_model=dict)
async def publish_to_web_bulk(
    blocks: List[SEOBlock],
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    """Publish many generated pages to public /p/{slug} URLs in one call."""
    from services.publish_pipeline import track_public_publish, maybe_auto_create_ads

    base = _public_base(request)
    published = []
    for block in blocks:
        slug = _block_slug(block)
        block.slug = slug
        result = await session.execute(select(PageRecord).where(PageRecord.slug == slug))
        existing = result.scalar_one_or_none()
        if existing:
            existing.seo_block = block.model_dump()
            existing.updated_at = datetime.now(timezone.utc)
        else:
            session.add(PageRecord(
                business_type=block.business_type,
                base_location=f"{block.city}, {block.state}",
                city=block.city, state=block.state or "", slug=slug,
                seo_block=block.model_dump(),
            ))
        public_url = f"{base}/{slug}"
        indexing = await track_public_publish(url=public_url, block=block, session=session)
        ads = await maybe_auto_create_ads(public_url=public_url, block=block)
        published.append({
            "slug": slug, "city": block.city, "state": block.state,
            "title": block.title, "public_url": public_url,
            "indexing": indexing, "ads": ads,
        })
    await session.commit()
    try:
        from services.sitemap_service import persist_live_sitemaps
        await persist_live_sitemaps(session, site_base=base)
    except Exception:
        pass
    return {
        "published": published,
        "count": len(published),
        "automation": {
            "ads_auto_create": bool(settings.GOOGLE_ADS_AUTO_CREATE_ON_PUBLISH),
            "ads_auto_enable": bool(settings.GOOGLE_ADS_AUTO_ENABLE),
        },
    }

@router.post("/save", response_model=dict)
async def save_page(
    business_type: str,
    city: str,
    state: str = "CA",
    session: AsyncSession = Depends(get_session),
):
    block = await generate_seo_block(business_type, city, state)
    return await _upsert_block(session, business_type, city, state, block)


class SaveBlockRequest(BaseModel):
    block: SEOBlock
    apply_globally: bool = True
    business_type: str = ""
    sibling_slugs: List[str] = []
    sibling_blocks: List[SEOBlock] = []


def _relocalize_text(text: str, src: SEOBlock, dest_city: str, dest_state: str, dest_zip: str, keep_zip: bool = False) -> str:
    if not text:
        return text
    out = text
    src_zip = (src.zip or "").strip()
    # ZIP must never be copied into title/body — only FAQ answers keep it.
    if src_zip and dest_zip and src_zip != dest_zip and keep_zip:
        out = out.replace(src_zip, dest_zip)
    src_city = (src.city or "").strip()
    if src_city and dest_city and src_city.lower() != dest_city.lower():
        out = re.sub(re.escape(src_city), dest_city, out, flags=re.I)
    src_state = (src.state or "").strip()
    if src_state and dest_state and src_state.upper() != dest_state.upper():
        out = re.sub(rf"\b{re.escape(src_state)}\b", dest_state, out)
    return out


def _relocalize_block(src: SEOBlock, dest: dict, dest_city: str, dest_state: str, dest_zip: str) -> dict:
    """Copy edited global copy onto a sibling location page, swapping place names."""
    out = dict(dest or {})
    text_fields = ("title", "h1", "intro", "content", "meta_description", "cta")
    for field in text_fields:
        src_val = getattr(src, field, None)
        if src_val:
            out[field] = _relocalize_text(src_val, src, dest_city, dest_state, dest_zip, keep_zip=False)
    if src.h2s:
        out["h2s"] = [_relocalize_text(h, src, dest_city, dest_state, dest_zip, keep_zip=False) for h in src.h2s]
    if src.h3s:
        out["h3s"] = [_relocalize_text(h, src, dest_city, dest_state, dest_zip, keep_zip=False) for h in src.h3s]
    if src.faqs:
        faqs = []
        for faq in src.faqs:
            q = faq.question if hasattr(faq, "question") else (faq or {}).get("question", "")
            a = faq.answer if hasattr(faq, "answer") else (faq or {}).get("answer", "")
            faqs.append({
                "question": _relocalize_text(q, src, dest_city, dest_state, dest_zip, keep_zip=False),
                "answer": _relocalize_text(a, src, dest_city, dest_state, dest_zip, keep_zip=True),
            })
        out["faqs"] = faqs
    out["city"] = dest_city
    out["state"] = dest_state
    if dest_zip:
        out["zip"] = dest_zip
    from services.zeorbit_local_seo import strip_zip_from_copy, ensure_zip_in_last_faq
    for field in text_fields:
        if out.get(field):
            out[field] = strip_zip_from_copy(out[field], dest_zip)
    if out.get("h2s"):
        out["h2s"] = [strip_zip_from_copy(h, dest_zip) for h in out["h2s"]]
    if out.get("h3s"):
        out["h3s"] = [strip_zip_from_copy(h, dest_zip) for h in out["h3s"]]
    out["faqs"] = ensure_zip_in_last_faq(out.get("faqs") or [], dest_city, dest_state, dest_zip)
    return out


async def _upsert_block(session, business_type: str, city: str, state: str, block: SEOBlock):
    slug = (block.slug or "").strip() or slugify(f"{business_type}-{city}")
    block.slug = slug
    result = await session.execute(select(PageRecord).where(PageRecord.slug == slug))
    existing = result.scalar_one_or_none()
    payload = block.model_dump()
    if existing:
        existing.seo_block = payload
        try:
            from sqlalchemy.orm.attributes import flag_modified
            flag_modified(existing, "seo_block")
        except Exception:
            pass
        existing.updated_at = datetime.now(timezone.utc)
        existing.business_type = business_type or existing.business_type
        existing.city = city
        existing.state = state
    else:
        session.add(PageRecord(
            business_type=business_type,
            base_location=f"{city}, {state}".strip(", "),
            city=city,
            state=state,
            slug=slug,
            seo_block=payload,
        ))
    await session.commit()
    return {"slug": slug, "saved": True}


@router.post("/save-block", response_model=dict)
async def save_block(req: SaveBlockRequest, session: AsyncSession = Depends(get_session)):
    """Persist the edited SEO block. Optionally apply the same copy to sibling location pages."""
    block = req.block
    bt = (req.business_type or block.business_type or "").strip()
    saved = await _upsert_block(session, bt, block.city, block.state or "CA", block)
    updated = 1
    if req.sibling_blocks:
        for sib in req.sibling_blocks:
            if not (sib.city or "").strip():
                continue
            if (sib.slug or "").strip() == saved["slug"]:
                continue
            await _upsert_block(session, bt or (sib.business_type or ""), sib.city, sib.state or "CA", sib)
            updated += 1
    elif req.apply_globally:
        kind = (block.content_type or "service").lower()
        slug_set = {s.strip() for s in (req.sibling_slugs or []) if (s or "").strip()}
        if slug_set:
            rows = (await session.execute(select(PageRecord).where(PageRecord.slug.in_(slug_set)))).scalars().all()
        elif bt:
            rows = (await session.execute(select(PageRecord).where(PageRecord.business_type == bt))).scalars().all()
        else:
            rows = []
        from sqlalchemy.orm.attributes import flag_modified
        for row in rows:
            if (row.slug or "") == saved["slug"]:
                continue
            dest = row.seo_block if isinstance(row.seo_block, dict) else {}
            dest_kind = (dest.get("content_type") or "service").lower()
            if dest_kind != kind:
                continue
            dest_city = row.city or dest.get("city") or ""
            dest_state = row.state or dest.get("state") or ""
            dest_zip = dest.get("zip") or ""
            if not dest_city:
                continue
            row.seo_block = _relocalize_block(block, dest, dest_city, dest_state, dest_zip)
            try:
                flag_modified(row, "seo_block")
            except Exception:
                pass
            row.updated_at = datetime.now(timezone.utc)
            updated += 1
        await session.commit()
    saved["updated_count"] = updated
    saved["applied_globally"] = bool(req.apply_globally)
    return saved

@router.get("/blog", response_model=dict)
async def list_blog_posts(
    request: Request,
    skip: int = 0,
    limit: int = 24,
    session: AsyncSession = Depends(get_session),
):
    """
    Public blog feed for the marketing site.
    Lists SEO content published to this app (/p/{slug}) plus tracked live WordPress URLs.
    """
    base = _public_base(request)
    limit = max(1, min(limit, 100))
    skip = max(0, skip)

    page_result = await session.execute(
        select(PageRecord).order_by(PageRecord.created_at.desc()).limit(3000)
    )
    page_rows = page_result.scalars().all()
    by_slug = {r.slug: r for r in page_rows if r.slug}

    posts = []
    seen_paths = set()

    def _add_post(item: dict):
        path = (item.get("url") or "").rstrip("/") or item.get("slug") or ""
        key = path.lower()
        if not key or key in seen_paths:
            return
        seen_paths.add(key)
        posts.append(item)

    for r in page_rows:
        block = r.seo_block if isinstance(r.seo_block, dict) else {}
        if not _is_blog_block(block):
            continue
        title = (block.get("title") or block.get("h1") or r.business_type or "Untitled").strip()
        excerpt = _plain_excerpt(block, title)
        raw_ind = (block.get("industry") or "").strip()
        if raw_ind.lower() in {
            "", "professional services", "other", "services", "local services", "digital services",
        }:
            category = (r.business_type or block.get("business_type") or "SEO").strip()
        else:
            category = raw_ind
        _add_post({
            "id": f"page-{r.id}",
            "source": "web",
            "title": title,
            "excerpt": excerpt,
            "category": category,
            "slug": r.slug,
            "url": f"/{r.slug}",
            "public_url": f"{base}/{r.slug}",
            "city": r.city,
            "state": r.state,
            "featured_image_url": block.get("featured_image_url") or None,
            "published_at": (r.updated_at or r.created_at).isoformat() if (r.updated_at or r.created_at) else None,
        })

    try:
        wp_result = await session.execute(
            select(PublishedUrlRecord)
            .where(PublishedUrlRecord.status != "error")
            .order_by(PublishedUrlRecord.created_at.desc())
            .limit(400)
        )
        _test_landing = re.compile(
            r"^/(contractors|healthcare|web-design|plumbing|software-engineer|"
            r"local-service|website-redesign|education)[-/]",
            re.I,
        )
        for u in wp_result.scalars().all():
            if not u.url:
                continue
            parsed = urlparse(u.url if "://" in u.url else f"https://{u.url}")
            host = (parsed.hostname or "").lower()
            if "nip.io" in host or host.startswith("seo.") or host.endswith(".nip.io"):
                continue
            path = (parsed.path or "").rstrip("/") or "/"
            if _test_landing.search(path):
                continue
            slug = ""
            if path.startswith("/p/"):
                slug = path.rsplit("/", 1)[-1]
                if _test_landing.search(f"/{slug}"):
                    continue
                live = _rewrite_reader_url(u.url, slug)
                rel = f"/{slug}"
            else:
                if host and "zeorbit.com" not in host:
                    continue
                if path in ("", "/", "/blog", "/website-designing", "/mobile-apps", "/seo-ppc",
                            "/custom-software", "/portfolio", "/contact"):
                    continue
                slug = path.strip("/")
                live = _rewrite_reader_url(u.url, slug)
                rel = f"/{slug}" if slug else live
            row = by_slug.get(slug) if slug else None
            block = row.seo_block if row and isinstance(row.seo_block, dict) else {}
            title = (u.title or (block.get("title") if block else "") or slug or u.url).strip()
            excerpt = _plain_excerpt(block, title)
            feat = (block.get("featured_image_url") if block else None) or None
            category = "Published"
            if block:
                raw_ind = (block.get("industry") or "").strip()
                category = raw_ind or (row.business_type if row else "Published") or "Published"
            _add_post({
                "id": f"wp-{u.id}",
                "source": u.source or "wordpress",
                "title": title,
                "excerpt": excerpt,
                "category": category,
                "slug": slug,
                "url": rel,
                "public_url": live,
                "city": (row.city if row else "") or "",
                "state": (row.state if row else "") or "",
                "featured_image_url": feat,
                "published_at": u.created_at.isoformat() if u.created_at else None,
            })
    except Exception:
        pass

    posts.sort(key=lambda p: p.get("published_at") or "", reverse=True)
    total = len(posts)
    slice_posts = posts[skip: skip + limit]

    return {
        "posts": slice_posts,
        "total": total,
        "skip": skip,
        "limit": limit,
    }


@router.post("/admin/dedupe-images", response_model=dict)
async def dedupe_page_images(
    session: AsyncSession = Depends(get_session),
):
    """One-shot: reassign featured images so pages/blogs don't share the same Unsplash photo."""
    from services.image_service import reassign_unique_featured_images
    result = await session.execute(select(PageRecord).order_by(PageRecord.created_at.asc()))
    rows = result.scalars().all()
    updated = await reassign_unique_featured_images(rows)
    await session.commit()
    return {"updated": updated, "total": len(rows)}


@router.get("/", response_model=List[dict])
async def list_pages(
    request: Request,
    skip: int = 0,
    limit: int = 20,
    session: AsyncSession = Depends(get_session),
):
    limit = max(1, min(int(limit or 20), 250))
    skip = max(0, int(skip or 0))
    result = await session.execute(
        select(PageRecord).offset(skip).limit(limit).order_by(PageRecord.created_at.desc())
    )
    rows = result.scalars().all()
    base = _public_base(request)
    return [
        {
            "id": r.id,
            "business_type": r.business_type,
            "base_location": r.base_location,
            "city": r.city,
            "state": r.state,
            "slug": r.slug,
            "seo_block": r.seo_block,
            "public_url": f"{base}/{r.slug}",
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in rows
    ]

@router.get("/{slug}", response_model=dict)
async def get_page(slug: str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(PageRecord).where(PageRecord.slug == slug))
    row = result.scalar_one_or_none()
    if not row:
        raise HTTPException(status_code=404, detail="Page not found")
    return {
        "id": row.id,
        "business_type": row.business_type,
        "city": row.city,
        "state": row.state,
        "slug": row.slug,
        "seo_block": row.seo_block,
        "public_url": f"{_reader_base()}/{row.slug}",
        "created_at": row.created_at.isoformat() if row.created_at else None,
    }

@router.delete("/{slug}")
async def delete_page(slug: str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(delete(PageRecord).where(PageRecord.slug == slug))
    await session.commit()
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Page not found")
    return {"deleted": True}
