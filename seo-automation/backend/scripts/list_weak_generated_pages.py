#!/usr/bin/env python3
"""
List auto-generated location pages that look thin/duplicate (master rule §25).

Does NOT delete anything. Review the report, then delete/regenerate deliberately.

Usage:
  cd seo-automation/backend
  ./venv/bin/python scripts/list_weak_generated_pages.py
  ./venv/bin/python scripts/list_weak_generated_pages.py --json
"""
from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from db import AsyncSessionLocal, PageRecord
from services.zeorbit_local_seo import content_similarity, score_page_quality


WEAK_MARKERS = (
    "contact us today",
    "provides affordable website design in",
    "zeorbit provides website design in",
)


async def main(as_json: bool = False) -> None:
    async with AsyncSessionLocal() as session:
        rows = (await session.execute(select(PageRecord))).scalars().all()

    bodies = []
    flagged = []
    for row in rows:
        block = row.seo_block if isinstance(row.seo_block, dict) else {}
        if (block.get("content_type") or "service") == "blog":
            continue
        intro = block.get("intro") or ""
        content = block.get("content") or ""
        body = f"{intro}\n{content}".strip()
        title = block.get("title") or ""
        city = row.city or block.get("city") or ""
        imgs = block.get("in_content_images") or []
        feat = block.get("featured_image_url") or ""
        alt = ""
        if imgs:
            alt = (imgs[0] or {}).get("alt_text") if isinstance(imgs[0], dict) else ""
        q = score_page_quality(
            title=title,
            intro=intro,
            content=content,
            faqs=block.get("faqs") or [],
            city=city,
            intent_id=block.get("search_intent") or "",
            image_url=feat,
            image_alt=alt or "",
            image_concept_text=block.get("image_concept") or "",
            meta=block.get("meta_description") or "",
            existing_bodies=bodies,
        )
        thin = len(body.split()) < 280
        marker = any(m in body.lower() for m in WEAK_MARKERS)
        dup = any(content_similarity(body, b) >= 0.72 for b in bodies)
        tourism_img = any(
            t in (alt or "").lower() or t in (feat or "").lower()
            for t in ("beach", "hotel", "picsum", "skyline")
        )
        if thin or marker or dup or tourism_img or not q.publishable:
            flagged.append({
                "slug": row.slug,
                "city": city,
                "title": title,
                "words": len(body.split()),
                "quality_score": q.score,
                "publishable": q.publishable,
                "reasons": q.reasons
                + (["thin_copy"] if thin else [])
                + (["weak_marker"] if marker else [])
                + (["near_duplicate"] if dup else [])
                + (["tourism_image"] if tourism_img else []),
                "featured_image_url": feat,
            })
        if body:
            bodies.append(body)

    if as_json:
        print(json.dumps({"count": len(flagged), "pages": flagged}, indent=2))
        return

    print(f"Flagged {len(flagged)} of {len(rows)} pages (no deletions performed)\n")
    for item in flagged:
        print(f"- {item['slug']} | {item['city']} | score={item['quality_score']} | {', '.join(item['reasons'])}")
        print(f"  {item['title'][:90]}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    asyncio.run(main(as_json=args.json))
