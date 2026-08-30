import uuid
import re
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.schemas import (
    GenerateRequest, SEOBlock, BulkGenerateResponse,
    ArticleRequest, WebsiteAnalysisRequest, WebsiteProfile, CityInfo,
    BriefSuggestRequest, BriefSuggestResponse,
)
from services.location_service import get_nearby_cities, LocationNotResolvedError, merge_extra_locations, resolve_generation_cities
from services.content_service import generate_seo_block, generate_seo_block_until_floor, generate_articles
from services.website_analysis_service import analyze_website
from services.export_service import export_json, export_html, export_wordpress
from db import get_session, PageRecord
from datetime import datetime, timezone
from typing import List, Optional

router = APIRouter()

def slugify(text: str) -> str:
    return re.sub(r'[^a-z0-9-]+', '-', text.lower()).strip('-')

from services.llm_service import available_providers

@router.get("/llm-providers")
async def llm_providers():
    """Return which AI models are configured so the UI can enable/disable options."""
    return available_providers()


def _compose_brief_text(data: dict) -> str:
    parts = []
    if data.get("topic_title"):
        parts.append(f"Working title / topic: {data['topic_title'].strip()}")
    if data.get("search_intent"):
        parts.append(f"Search intent: {data['search_intent'].strip()}")
    if data.get("customer_problem"):
        parts.append(f"Customer problem: {data['customer_problem'].strip()}")
    if data.get("pricing"):
        parts.append(f"Pricing: {data['pricing'].strip()}")
    if data.get("key_points"):
        parts.append(f"Key points to cover:\n{data['key_points'].strip()}")
    if data.get("faq_ideas"):
        parts.append(f"FAQs to answer:\n{data['faq_ideas'].strip()}")
    if data.get("cta_direction"):
        parts.append(f"CTA direction: {data['cta_direction'].strip()}")
    if data.get("tone_notes"):
        parts.append(f"Tone / voice notes: {data['tone_notes'].strip()}")
    if data.get("extra_notes"):
        parts.append(f"Extra editor notes:\n{data['extra_notes'].strip()}")
    return "\n\n".join(parts).strip()


def _brief_needs_autofill(brief: str) -> bool:
    text = (brief or "").strip()
    if len(text) < 40:
        return True
    has_pricing = bool(re.search(r"(?im)^\s*pricing\s*:", text) or re.search(r"\$\s*\d", text))
    has_intent = bool(re.search(r"(?im)^\s*search intent\s*:", text))
    has_problem = bool(re.search(r"(?im)^\s*customer problem\s*:", text))
    return not (has_pricing and has_intent and has_problem)


async def ensure_brief_for_generate(req: GenerateRequest) -> GenerateRequest:
    """
    Minimal UI path: keyword + niche + location.
    Always compose the structured brief from the master instruction when thin/missing.
    """
    from services.zeorbit_local_seo import ZEORBIT_FACTS, resolve_industry_label, is_generic_industry

    # Never invent "Professional Services" — infer a real vertical from niche/keywords, else leave blank
    if not (req.industry or "").strip() or is_generic_industry(req.industry):
        req.industry = resolve_industry_label(
            "", req.business_type or "", list(req.target_keywords or [])
        )
    if not (req.audience or "").strip():
        req.audience = "Small business owners"

    brief = (req.custom_requirements or "").strip()
    if not _brief_needs_autofill(brief):
        return req

    suggest_req = BriefSuggestRequest(
        content_kind=req.content_kind,
        business_type=req.business_type or "",
        industry=req.industry or "",
        audience=req.audience or "",
        base_location=req.base_location or ((req.extra_locations or [""])[0] if req.extra_locations else ""),
        target_keywords=list(req.target_keywords or []),
        extra_notes=brief,
        field="all",
        llm_provider=req.llm_provider,
    )
    base = _template_brief_fields(suggest_req)
    try:
        from services.llm_service import chat_json, llm_available
        from services.master_custom_instruction import master_instruction_for_prompt
        # Prefer LLM whenever available — frontend no longer sends a brief
        if llm_available():
            place = suggest_req.base_location or "United States"
            kind = "blog post" if req.content_kind == "post" else "location / service page"
            blog_extra = ""
            if req.content_kind == "post":
                kw0 = (req.target_keywords or ["the search query"])[0]
                blog_extra = f"""
BLOG-ONLY RULE: topic_title, search_intent, customer_problem, key_points, and faq_ideas MUST be about the editor's keyword/query "{kw0}".
Do not rewrite it into a location page or generic web-design sales brief. Answer that query.
"""
            prompt = f"""You fill a ZeOrbit content brief for a {kind}.
Follow this MASTER CUSTOM INSTRUCTION exactly (this is the format and rule set):
{master_instruction_for_prompt(6500)}
{blog_extra}
Business niche: {req.business_type or "Web Design"}
Industry (client type — examples only for blogs): {req.industry or "infer from keyword + niche"}
Audience (infer if blank): {req.audience or "infer from keyword + niche"}
Location: {place}
Keywords (for blogs this IS the article subject): {', '.join(req.target_keywords) or 'website design'}

Return ONLY JSON:
{{
  "topic_title": "working title that names the keyword/query",
  "search_intent": "short intent label matched to the keyword",
  "customer_problem": "1-2 sentences about the searcher's problem for this query",
  "pricing": "{ZEORBIT_FACTS['pricing_range']}",
  "key_points": "5-7 bullet lines starting with - that teach the query",
  "faq_ideas": "4-6 bullet questions starting with - about the query",
  "cta_direction": "1 soft CTA sentence",
  "tone_notes": "1-2 sentences on voice",
  "industry": "inferred industry label if helpful",
  "audience": "inferred audience label if helpful"
}}"""
            data = await chat_json(prompt, temperature=0.55, max_tokens=1400, provider=req.llm_provider)
            if data:
                for key in ("topic_title", "search_intent", "customer_problem", "pricing", "key_points", "faq_ideas", "cta_direction", "tone_notes"):
                    val = data.get(key)
                    if isinstance(val, str) and val.strip():
                        base[key] = val.strip()
                    elif isinstance(val, list):
                        base[key] = "\n".join(f"- {x}" for x in val if x)
                if isinstance(data.get("industry"), str) and data["industry"].strip():
                    from services.zeorbit_local_seo import is_generic_industry, resolve_industry_label
                    inferred = data["industry"].strip()
                    if not is_generic_industry(inferred):
                        req.industry = inferred
                    elif not (req.industry or "").strip():
                        req.industry = resolve_industry_label(
                            "", req.business_type or "", list(req.target_keywords or [])
                        )
                if isinstance(data.get("audience"), str) and data["audience"].strip():
                    req.audience = data["audience"].strip()
    except Exception as e:
        print(f"[Generate] brief autofill AI failed, using template: {e}")

    if not (base.get("pricing") or "").strip():
        base["pricing"] = ZEORBIT_FACTS["pricing_range"]
    if brief and "Extra editor notes" not in brief:
        base["extra_notes"] = brief
    req.custom_requirements = _compose_brief_text(base)
    return req


def _template_brief_fields(req: BriefSuggestRequest) -> dict:
    from services.zeorbit_local_seo import (
        pick_search_intent,
        format_title,
        intent_faqs,
        ZEORBIT_FACTS,
        pick_industry,
    )
    city = (req.base_location or "").split(",")[0].strip() or "your area"
    industry = pick_industry(req.industry or "", city, 0)
    intent = pick_search_intent(
        city, 0, industry=industry, brief=req.extra_notes or req.topic_title or "", keywords=req.target_keywords or [],
    )
    if req.search_intent:
        # Keep user-chosen intent label if provided
        intent_label = req.search_intent
    else:
        intent_label = intent.label
    title = req.topic_title or format_title(intent, city, industry, 0)
    problem = req.customer_problem or (
        f"Businesses in {city} ({industry or 'small business'}) that {intent.customer_problem}."
    )
    key_points = req.key_points or "\n".join([
        f"- Who ZeOrbit helps in {city} and what problem this page solves",
        f"- Relevant services: WordPress, Shopify, redesign, mobile-friendly sites, SEO-friendly structure",
        f"- Pricing context: website projects typically {ZEORBIT_FACTS['pricing_range']}",
        f"- Experience: {ZEORBIT_FACTS['experience']}, {ZEORBIT_FACTS['reviews']}",
        f"- Practical advice for choosing a website provider",
        f"- Clear next step / CTA",
    ])
    faqs = intent_faqs(intent, city, industry, 0)
    faq_ideas = req.faq_ideas or "\n".join(f"- {f['question']}" for f in faqs[:5])
    cta = req.cta_direction or (
        f"Invite a conversation about a reasonably priced website for a {industry or 'small business'} in {city}. Soft CTA — not a hard sell."
    )
    tone = req.tone_notes or (
        "Plain American English for a small-business owner. No fluff (cutting-edge, seamless, unlock your potential). "
        "Do not invent fake reviews, offices, or 'best in city' claims."
    )
    pricing = (req.pricing or "").strip() or ZEORBIT_FACTS["pricing_range"]
    return {
        "topic_title": title,
        "search_intent": intent_label,
        "customer_problem": problem,
        "pricing": pricing,
        "key_points": key_points,
        "faq_ideas": faq_ideas,
        "cta_direction": cta,
        "tone_notes": tone,
        "extra_notes": req.extra_notes or "",
    }


@router.post("/suggest-brief", response_model=BriefSuggestResponse)
async def suggest_brief(req: BriefSuggestRequest):
    """Fill structured Page/Post brief fields with AI (or templates if no LLM)."""
    from services.llm_service import chat_json, llm_available
    from services.master_custom_instruction import master_instruction_for_prompt

    base = _template_brief_fields(req)
    field = (req.field or "all").strip().lower()
    source = "template"

    if llm_available():
        place = req.base_location or "United States"
        kind = "blog post" if req.content_kind == "post" else "location / service page"
        prompt = f"""You help an editor fill a structured content brief for ZeOrbit ({kind}).
Follow this MASTER CUSTOM INSTRUCTION when choosing intent, problem, FAQs, CTA, and tone:
{master_instruction_for_prompt(4500)}

Business niche: {req.business_type or "Web Design"}
Industry (client type): {req.industry or "small business"}
Audience: {req.audience or "small business owners"}
Location: {place}
Keywords: {', '.join(req.target_keywords) or 'website design'}
Existing notes: {req.extra_notes or 'none'}

Return ONLY JSON with these keys (short, editable draft text — not the full article):
{{
  "topic_title": "working title",
  "search_intent": "short intent matched to the keyword (e.g. WordPress | Website redesign | Mobile app | SEO | eCommerce)",
  "customer_problem": "1-2 sentences: what the customer is trying to solve",
  "pricing": "typical project range, e.g. $500–$3,000 — only when website-related",
  "key_points": "5-7 bullet lines starting with -",
  "faq_ideas": "4-6 bullet questions starting with -",
  "cta_direction": "1 sentence soft CTA guidance",
  "tone_notes": "1-2 sentences on voice"
}}

Rules: match services to the keyword (do not force every ZeOrbit service). Default website pricing $500–$3,000 when applicable. No fake reviews/offices/#1 claims. Field focus: {field}."""
        try:
            data = await chat_json(prompt, temperature=0.7, max_tokens=1200, provider=req.llm_provider)
            if data:
                source = "ai"
                for key in ("topic_title", "search_intent", "customer_problem", "pricing", "key_points", "faq_ideas", "cta_direction", "tone_notes"):
                    if field != "all" and field != key:
                        continue
                    val = data.get(key)
                    if isinstance(val, str) and val.strip():
                        base[key] = val.strip()
                    elif field == "all" and isinstance(val, list):
                        base[key] = "\n".join(f"- {x}" for x in val if x)
        except Exception as e:
            print(f"[Brief] AI suggest failed, using template: {e}")

    if field != "all" and field in base:
        # Only return the requested field change; keep others from request if provided
        for key in ("topic_title", "search_intent", "customer_problem", "pricing", "key_points", "faq_ideas", "cta_direction", "tone_notes"):
            if key == field:
                continue
            incoming = getattr(req, key, "") or ""
            if incoming.strip():
                base[key] = incoming.strip()

    composed = _compose_brief_text(base)
    return BriefSuggestResponse(**base, composed_brief=composed, source=source)


async def _places_for_generate(req: GenerateRequest) -> List:
    """Pages require locations. Posts may be a single topic article with no city."""
    try:
        cities = await resolve_generation_cities(req.base_location, req.num_cities, req.extra_locations)
    except LocationNotResolvedError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if req.content_kind != "post":
        from services.location_service import lookup_place_zip
        from services.zeorbit_local_seo import digits_zip
        fallback = ""
        if req.base_location:
            base = (req.base_location or "").strip()
            # "Solana Beach, CA" or "... 92075"
            fallback = digits_zip(base)
            if not fallback and "," in base:
                city_part, _, rest = base.partition(",")
                st_m = re.search(r"\b([A-Za-z]{2})\b", rest)
                st = (st_m.group(1) if st_m else rest.strip()[:2]).upper()
                fallback = digits_zip(await lookup_place_zip(city_part.strip(), st, ""))
        required: List = []
        missing_names: List[str] = []
        for c in cities:
            z = digits_zip(getattr(c, "zip", "") or "")
            if not z:
                z = digits_zip(await lookup_place_zip(c.name, c.state or "", getattr(c, "zip", "") or ""))
            if z:
                c.zip = z
                if not fallback:
                    fallback = z
                required.append(c)
            else:
                missing_names.append(f"{c.name}, {c.state}".strip(", "))
                required.append(c)
        if fallback:
            for c in required:
                if not digits_zip(getattr(c, "zip", "") or ""):
                    c.zip = fallback
                    print(f"[Location] inherited ZIP {fallback} for {c.name}")
        still_missing = [
            f"{c.name}, {c.state}".strip(", ")
            for c in required
            if not digits_zip(getattr(c, "zip", "") or "")
        ]
        if not required:
            detail = "ZIP is mandatory for every location page."
            if missing_names:
                detail += " Could not resolve a ZIP for: " + "; ".join(missing_names[:12])
            raise HTTPException(status_code=400, detail=detail)
        if still_missing:
            print(f"[Location] still no ZIP after inherit: {still_missing}")
        cities = required
    if cities:
        return cities
    if req.content_kind == "post":
        return [CityInfo(name="", state="", country="US", latitude=0.0, longitude=0.0, kind="city")]
    raise HTTPException(status_code=400, detail="Add at least one location (base city or bulk communities).")


@router.post("/generate", response_model=BulkGenerateResponse)
async def generate_bulk(req: GenerateRequest, session: AsyncSession = Depends(get_session)):
    """Generate location pages/posts. Regenerates any result below 90% until it passes."""
    from services.zeorbit_local_seo import MIN_PUBLISH_SCORE, MIN_KEYWORD_USE_SCORE, scores_meet_floor

    req = await ensure_brief_for_generate(req)
    cities = await _places_for_generate(req)
    requested_n = len(cities)

    pages: List[SEOBlock] = []
    retried_n = 0
    used_featured: List[str] = []
    existing_bodies: List[str] = []
    # Avoid colliding with images already saved for other locations (featured + body)
    from services.image_service import normalize_image_key, generate_article_images, topic_image_family
    existing_rows = (await session.execute(select(PageRecord))).scalars().all()
    # slug -> row for O(1) upserts (preview slug and final slug can differ)
    by_slug = { (row.slug or "").strip(): row for row in existing_rows if (row.slug or "").strip() }
    niche_family = topic_image_family(req.business_type)
    for row in existing_rows:
        block0 = row.seo_block if isinstance(row.seo_block, dict) else {}
        row_family = topic_image_family(
            f"{row.business_type or ''} {(block0 or {}).get('business_type') or ''}"
        )
        # Blog posts all share website stock — exclude every published photo, not just same niche
        if req.content_kind != "post":
            if niche_family and row_family and niche_family != row_family:
                continue
        url0 = (block0 or {}).get("featured_image_url") or ""
        if url0:
            used_featured.append(url0)
        for im in (block0 or {}).get("in_content_images") or []:
            if isinstance(im, dict) and im.get("url"):
                used_featured.append(im["url"])
            elif hasattr(im, "url") and im.url:
                used_featured.append(im.url)
        body0 = f"{(block0 or {}).get('intro') or ''}\n{(block0 or {}).get('content') or ''}".strip()
        if body0:
            existing_bodies.append(body0)

    batch_slugs: set[str] = set()

    for keyword_index, city_info in enumerate(cities):
        exclude = list(used_featured)
        from services.slug_utils import article_slug
        from services.content_service import pick_primary_keyword, article_topic
        focus = (
            article_topic(req.custom_requirements, req.target_keywords, req.business_type)
            if req.content_kind == "post"
            else pick_primary_keyword(
                req.target_keywords,
                req.business_type,
                city_info.name,
                keyword_index,
                industry=req.industry or "",
            )
        )
        preview_slug = article_slug(
            [focus] + list(req.target_keywords or []),
            city_info.name,
            focus,
        )
        # Free images from the row we are about to overwrite (preview OR any city match).
        candidates = []
        if preview_slug in by_slug:
            candidates.append(by_slug[preview_slug])
        for row in existing_rows:
            if (row.city or "").strip().lower() == (city_info.name or "").strip().lower():
                candidates.append(row)
        free_urls = []
        for cand in candidates:
            prev = cand.seo_block if isinstance(cand.seo_block, dict) else {}
            if (prev or {}).get("featured_image_url"):
                free_urls.append(prev["featured_image_url"])
            for im in (prev or {}).get("in_content_images") or []:
                u = im.get("url") if isinstance(im, dict) else getattr(im, "url", None)
                if u:
                    free_urls.append(u)
        if free_urls:
            free_keys = {normalize_image_key(u) for u in free_urls}
            exclude = [u for u in exclude if normalize_image_key(u) not in free_keys]

        try:
            block, extra_attempts = await generate_seo_block_until_floor(
            req.business_type,
            city_info.name,
            city_info.state,
            req.target_keywords,
            req.industry,
            use_ai=req.use_ai,
            llm_provider=req.llm_provider,
            exclude_image_urls=exclude,
            custom_requirements=req.custom_requirements,
            content_kind=req.content_kind,
            audience=req.audience,
            keyword_index=keyword_index,
            existing_bodies=existing_bodies,
            zip=getattr(city_info, "zip", "") or "",
            )
        except Exception as e:
            print(f"[Generate] {city_info.name} failed ({e}); writing a fallback page so none are skipped")
            block = await generate_seo_block(
                req.business_type,
                city_info.name,
                city_info.state,
                req.target_keywords,
                req.industry,
                use_ai=False,
                llm_provider=None,
                exclude_image_urls=exclude,
                custom_requirements=req.custom_requirements,
                content_kind=req.content_kind,
                audience=req.audience,
                keyword_index=keyword_index,
                zip=getattr(city_info, "zip", "") or "",
            )
            extra_attempts = 0
        if extra_attempts:
            retried_n += 1
            print(
                f"[Quality] {city_info.name} first scored below 90% — "
                f"generated again ({extra_attempts} extra pass(es))"
            )
        # Final uniqueness guard (same as async jobs path)
        if block.featured_image_url:
            taken = {normalize_image_key(u) for u in used_featured}
            key = normalize_image_key(block.featured_image_url)
            if key in taken:
                images = await generate_article_images(
                    focus,
                    f"{city_info.name}, {city_info.state} {getattr(city_info, 'zip', '') or ''}".strip(),
                    "ZeOrbit",
                    count=3,
                    exclude_urls=used_featured,
                    industry="" if req.content_kind == "post" else (req.industry or ""),
                    niche=focus if req.content_kind == "post" else (req.business_type or ""),
                    search_intent=getattr(block, "search_intent", "") or "",
                    image_concept_text=getattr(block, "image_concept", "") or "",
                    keyword_index=keyword_index,
                    content_type="blog" if req.content_kind == "post" else "service",
                    match_query=focus if req.content_kind == "post" else "",
                    audience=req.audience or "",
                )
                if images:
                    from services.image_service import assign_canonical_images
                    feat, foot, cleaned = assign_canonical_images(images)
                    # Never wipe a good image with an empty uniqueness regen
                    if feat:
                        block.in_content_images = cleaned
                        block.featured_image_url = feat
                        block.footer_image_url = foot
                    else:
                        print(f"[Image] uniqueness regen empty for {city_info.name}; keeping prior featured")
            # Prefer unique featured across pages; body images may reuse after pool stretch
            if block.featured_image_url:
                used_featured.append(block.featured_image_url)

        # Track bodies for in-batch duplicate detection
        existing_bodies.append(f"{block.intro or ''}\n{block.content or ''}")

        slug = (block.slug or preview_slug).strip()
        # Avoid in-batch duplicate inserts (same resolved place listed twice)
        if slug in batch_slugs:
            n = 2
            while f"{slug}-{n}" in batch_slugs or f"{slug}-{n}" in by_slug:
                n += 1
            slug = f"{slug}-{n}"
        batch_slugs.add(slug)
        block.slug = slug
        pages.append(block)

        # Upsert by FINAL slug — preview_slug often differs once industry is applied,
        # which previously caused UNIQUE constraint failures on INSERT.
        existing = by_slug.get(slug)
        if existing is None and preview_slug and preview_slug != slug:
            # Same city previously saved under an older slug form — update that row
            # and retarget its slug instead of inserting a duplicate.
            existing = by_slug.get(preview_slug)
        if existing is None:
            for row in existing_rows:
                if (
                    (row.city or "").strip().lower() == (city_info.name or "").strip().lower()
                    and (row.business_type or "").strip().lower() == (req.business_type or "").strip().lower()
                ):
                    existing = row
                    break

        payload = block.model_dump()
        if existing:
            old_slug = (existing.slug or "").strip()
            existing.seo_block = payload
            existing.business_type = req.business_type
            existing.base_location = req.base_location
            existing.city = city_info.name
            existing.state = city_info.state
            # Only retarget slug when the new slug is free
            if slug != old_slug and slug not in by_slug:
                if old_slug in by_slug:
                    by_slug.pop(old_slug, None)
                existing.slug = slug
                by_slug[slug] = existing
            elif slug != old_slug and slug in by_slug and by_slug[slug] is not existing:
                # Final slug already owned by another row — update that row instead
                target = by_slug[slug]
                target.seo_block = payload
                target.business_type = req.business_type
                target.base_location = req.base_location
                target.city = city_info.name
                target.state = city_info.state
                target.updated_at = datetime.now(timezone.utc)
            else:
                existing.slug = old_slug or slug
            existing.updated_at = datetime.now(timezone.utc)
        else:
            row = PageRecord(
                business_type=req.business_type,
                base_location=req.base_location,
                city=city_info.name,
                state=city_info.state,
                slug=slug,
                seo_block=payload,
            )
            session.add(row)
            by_slug[slug] = row
            existing_rows.append(row)

    if not pages:
        await session.rollback()
        raise HTTPException(status_code=502, detail="Generation produced no pages. Try again.")

    try:
        await session.commit()
    except Exception as e:
        await session.rollback()
        detail = str(e.orig) if getattr(e, "orig", None) else str(e)
        if "UNIQUE" in detail.upper() or "unique" in detail.lower():
            raise HTTPException(
                status_code=409,
                detail="A page with this URL slug already exists. Trash the old location page, or generate again — we will update it instead of duplicating.",
            )
        raise HTTPException(status_code=500, detail=f"Could not save generated pages: {detail[:240]}")

    dropped = max(0, requested_n - len(pages))
    msg = None
    if dropped:
        msg = (
            f"{len(pages)} of {requested_n} pages generated. "
            f"{dropped} did not complete — generate again for the missing ones."
        )
    elif retried_n > 0:
        msg = (
            f"{retried_n} location{'s' if retried_n != 1 else ''} first scored below "
            f"{int(MIN_PUBLISH_SCORE)}% — generated again, then kept all {len(pages)}."
        )

    return BulkGenerateResponse(
        total=len(pages),
        pages=pages,
        job_id=str(uuid.uuid4()),
        requested=requested_n,
        dropped=dropped,
        message=msg,
    )

@router.post("/analyze-website", response_model=WebsiteProfile)
async def analyze_website_endpoint(req: WebsiteAnalysisRequest):
    """Analyze a website URL: extract services, products, audience, tone, and page inventory."""
    return await analyze_website(req.website_url)


@router.post("/generate-articles", response_model=BulkGenerateResponse)
async def generate_articles_endpoint(req: ArticleRequest, session: AsyncSession = Depends(get_session)):
    """Generate N unique articles from a primary keyword + location, grounded in a website analysis."""
    profile = await analyze_website(req.website_url)
    try:
        pages = await generate_articles(req, profile)
    except LocationNotResolvedError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not pages:
        raise HTTPException(status_code=502, detail="Article generation failed. Check OPENAI_API_KEY.")

    city, _, _ = (req.location.partition(","))
    used_featured: List[str] = []
    from services.image_service import normalize_image_key
    for row in (await session.execute(select(PageRecord))).scalars().all():
        b0 = row.seo_block if isinstance(row.seo_block, dict) else {}
        u0 = (b0 or {}).get("featured_image_url") or ""
        if u0:
            used_featured.append(u0)

    for block in pages:
        # Namespace the slug so keyword-articles don't collide with city-page slugs.
        base_slug = block.slug or slugify(block.title)
        slug = base_slug
        result = await session.execute(select(PageRecord).where(PageRecord.slug == slug))
        existing = result.scalar_one_or_none()
        # Re-pick featured if it collides with another saved page
        feat = block.featured_image_url or ""
        if feat and normalize_image_key(feat) in {normalize_image_key(u) for u in used_featured}:
            from services.image_service import generate_article_images
            imgs = await generate_article_images(
                req.primary_keyword,
                f"{block.city or city.strip()}, {block.state or ''}".strip(", "),
                "",
                count=3,
                angle_title=block.title or "",
                exclude_urls=used_featured,
                industry=getattr(req, "industry", "") or getattr(block, "industry", "") or "",
                niche=req.primary_keyword or "",
            )
            if imgs:
                block.in_content_images = imgs
                block.featured_image_url = imgs[0].url
                feat = imgs[0].url
        if feat:
            used_featured.append(feat)
        if existing:
            existing.seo_block = block.model_dump()
            existing.updated_at = datetime.now(timezone.utc)
        else:
            session.add(PageRecord(
                business_type=req.primary_keyword,
                base_location=req.location,
                city=block.city or city.strip(),
                state=block.state or "",
                slug=slug,
                seo_block=block.model_dump(),
            ))
    await session.commit()

    return BulkGenerateResponse(total=len(pages), pages=pages, job_id=str(uuid.uuid4()))


@router.post("/generate/single", response_model=SEOBlock)
async def generate_single(
    business_type: str,
    city: str,
    state: str = "CA",
    use_ai: bool = False,
    llm_provider: str = None,
):
    return await generate_seo_block(business_type, city, state, use_ai=use_ai, llm_provider=llm_provider)


@router.post("/boost-scores", response_model=SEOBlock)
async def boost_scores(block: SEOBlock):
    """Raise Keyword use (and refresh Quality) toward the 90% floor — preview AI fix."""
    from services.content_service import boost_block_to_floor
    return boost_block_to_floor(block)


@router.post("/refresh-images")
async def refresh_images(
    slug: Optional[str] = None,
    only_unrelated: bool = True,
    dedupe: bool = False,
    session: AsyncSession = Depends(get_session),
):
    """Re-assign on-topic featured images for existing blogs without regenerating copy.

    Keeps all page content/titles/FAQs. Replaces featured_image_url + in_content_images only.
    By default only touches pages whose current image looks unrelated (Flickr/picsum/empty).
    Pass dedupe=true to reassign every page so featured photos are unique across the library.
    """
    from services.image_service import (
        generate_article_images,
        normalize_image_key,
        topic_image_family,
        stock_url_needs_replace,
        collect_image_urls_from_seo_block,
        assign_canonical_images,
    )
    from collections import defaultdict

    result = await session.execute(select(PageRecord))
    rows = result.scalars().all()
    updated = []
    skipped = []

    def _block_needs_image_refresh(block: dict) -> bool:
        urls = collect_image_urls_from_seo_block(block or {})
        if not urls:
            return True
        return any(stock_url_needs_replace(u) for u in urls)

    # When deduping, process all pages and never reuse a featured URL within a niche family.
    if dedupe and not slug:
        only_unrelated = False

    used_by_family: dict = defaultdict(list)
    if only_unrelated and not slug and not dedupe:
        for row in rows:
            block = row.seo_block if isinstance(row.seo_block, dict) else {}
            if not _block_needs_image_refresh(block):
                biz = row.business_type or block.get("business_type") or ""
                fam = topic_image_family(f"{biz} {block.get('title') or ''}")
                for u in collect_image_urls_from_seo_block(block):
                    if u:
                        used_by_family[fam].append(u)

    for row in rows:
        if slug and row.slug != slug:
            continue
        block = row.seo_block if isinstance(row.seo_block, dict) else {}
        if only_unrelated and not _block_needs_image_refresh(block) and not slug:
            skipped.append(row.slug)
            continue

        business = row.business_type or block.get("business_type") or ""
        city = row.city or block.get("city") or ""
        state = row.state or block.get("state") or ""
        kw = ""
        try:
            kw = (block.get("keywords") or {}).get("primary") or ""
        except Exception:
            kw = ""
        focus = kw or f"{business} {city}".strip()
        location = f"{city}, {state}".strip(", ")
        ctype = (block.get("content_type") or "").lower()
        is_blog = ctype in ("blog", "post") or not (city or "").strip()
        family = topic_image_family(
            f"{business} {focus} {block.get('title') or ''} {block.get('industry') or ''}"
        )
        images = await generate_article_images(
            focus, location, "", count=3,
            angle_title=block.get("title") or "",
            exclude_urls=used_by_family[family],
            industry="" if is_blog else (block.get("industry") or ""),
            niche=business,
            content_type="blog" if is_blog else "service",
            match_query=focus if is_blog else "",
            image_concept_text=block.get("image_concept") or "",
        )
        if not images:
            skipped.append(row.slug)
            continue

        feat2, foot2, cleaned = assign_canonical_images(images)
        block = dict(block)
        block["featured_image_url"] = feat2 or images[0].url
        block["footer_image_url"] = foot2
        block["in_content_images"] = [img.model_dump() if hasattr(img, "model_dump") else img for img in cleaned]
        row.seo_block = block
        try:
            from sqlalchemy.orm.attributes import flag_modified
            flag_modified(row, "seo_block")
        except Exception:
            pass
        row.updated_at = datetime.now(timezone.utc)
        # Exclude every assigned photo so the next location cannot reuse any of them
        for img in images:
            if img.url:
                used_by_family[family].append(img.url)
        updated.append({"slug": row.slug, "family": family, "featured_image_url": images[0].url})

    await session.commit()
    unique = len({normalize_image_key(p["featured_image_url"]) for p in updated})
    family_stats = {
        fam: len({normalize_image_key(u) for u in urls})
        for fam, urls in used_by_family.items()
    }
    return {
        "updated": len(updated),
        "skipped": len(skipped),
        "unique_featured_in_batch": unique,
        "unique_per_family": family_stats,
        "pages": updated[:50],
        "note": "Existing blog copy preserved — images only" + (" (deduped by niche)" if dedupe else ""),
    }


@router.post("/repair-images")
async def repair_block_images(block: dict):
    """Replace dead/placeholder Unsplash URLs on a draft block without rewriting copy."""
    from services.image_service import (
        generate_article_images,
        stock_url_needs_replace,
        collect_image_urls_from_seo_block,
        assign_canonical_images,
        normalize_image_key,
    )

    payload = dict(block or {})
    urls = collect_image_urls_from_seo_block(payload)
    unique_keys = {normalize_image_key(u) for u in urls if u}
    needs = (not urls) or any(stock_url_needs_replace(u) for u in urls) or len(unique_keys) < 3
    if not needs:
        return block

    business = payload.get("business_type") or ""
    city = payload.get("city") or ""
    state = payload.get("state") or ""
    kw = ""
    try:
        kw = (payload.get("keywords") or {}).get("primary") or ""
    except Exception:
        kw = ""
    focus = kw or f"{business} {city}".strip() or "website design"
    location = f"{city}, {state}".strip(", ")
    ctype = (payload.get("content_type") or "").lower()
    is_blog = ctype in ("blog", "post") or not (city or "").strip()
    images = await generate_article_images(
        focus, location, "", count=3,
        angle_title=payload.get("title") or "",
        industry="" if is_blog else (payload.get("industry") or ""),
        niche=business,
        content_type="blog" if is_blog else "service",
        match_query=focus if is_blog else "",
        image_concept_text=payload.get("image_concept") or "",
    )
    if not images:
        return block
    feat2, foot2, cleaned = assign_canonical_images(images)
    payload["featured_image_url"] = feat2 or images[0].url
    payload["footer_image_url"] = foot2
    payload["in_content_images"] = [
        img.model_dump() if hasattr(img, "model_dump") else img for img in cleaned
    ]
    return payload


@router.post("/export/json")
async def export_as_json(req: GenerateRequest):
    try:
        cities = await get_nearby_cities(req.base_location, req.num_cities)
    except LocationNotResolvedError as e:
        raise HTTPException(status_code=400, detail=str(e))
    pages = [await generate_seo_block(req.business_type, c.name, c.state) for c in cities]
    return JSONResponse(content={"pages": [p.model_dump() for p in pages]})

@router.post("/export/html")
async def export_as_html(business_type: str, city: str, state: str = "CA"):
    block = await generate_seo_block(business_type, city, state)
    html = export_html(block)
    return HTMLResponse(content=html)

@router.post("/export/wordpress")
async def export_as_wordpress(req: GenerateRequest):
    try:
        cities = await get_nearby_cities(req.base_location, req.num_cities)
    except LocationNotResolvedError as e:
        raise HTTPException(status_code=400, detail=str(e))
    pages = [await generate_seo_block(req.business_type, c.name, c.state) for c in cities]
    wp_posts = [export_wordpress(p) for p in pages]
    return {"posts": wp_posts}
