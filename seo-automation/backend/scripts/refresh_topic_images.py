#!/usr/bin/env python3
"""Re-assign on-topic curated images; never leave picsum placeholders."""
import asyncio
from sqlalchemy import select
from db import AsyncSessionLocal, PageRecord
from services.image_service import generate_article_images


async def main():
    async with AsyncSessionLocal() as s:
        rows = (await s.execute(select(PageRecord))).scalars().all()
        used = []
        updated = 0
        samples = []
        for r in rows:
            b = r.seo_block if isinstance(r.seo_block, dict) else {}
            slug = r.slug or ""
            feat = b.get("featured_image_url") or ""
            need = (
                "picsum.photos" in feat
                or slug.startswith("healthcare-")
                or slug.startswith("contractors-")
            )
            if not need:
                if feat:
                    used.append(feat)
                continue
            if "healthcare" in slug:
                industry = b.get("industry") or "Healthcare"
            elif "contractors" in slug:
                industry = b.get("industry") or "Contractors"
            else:
                industry = b.get("industry") or ""
            niche = r.business_type or b.get("business_type") or "WordPress Website Design"
            focus = b.get("focus_keyword") or niche
            loc = f"{r.city or ''}, {r.state or ''}".strip(", ")
            imgs = await generate_article_images(
                focus,
                loc,
                "ZeOrbit",
                count=3,
                exclude_urls=used[-40:],
                industry=industry,
                niche=niche,
            )
            if not imgs:
                continue
            # New dict so SQLAlchemy persists JSON column changes
            payload = dict(b)
            payload["featured_image_url"] = imgs[0].url
            payload["in_content_images"] = [im.model_dump() for im in imgs]
            r.seo_block = payload
            from sqlalchemy.orm.attributes import flag_modified
            flag_modified(r, "seo_block")
            used.append(imgs[0].url)
            updated += 1
            if len(samples) < 8:
                samples.append((slug, imgs[0].url[:90]))
        await s.commit()
        print("updated", updated)
        for slug, url in samples:
            print(slug, "->", url)
        rows = (await s.execute(select(PageRecord))).scalars().all()
        picsum = 0
        for r in rows:
            b = r.seo_block if isinstance(r.seo_block, dict) else {}
            if "picsum.photos" in str(b.get("featured_image_url") or ""):
                picsum += 1
        print("picsum remaining", picsum)


if __name__ == "__main__":
    asyncio.run(main())
