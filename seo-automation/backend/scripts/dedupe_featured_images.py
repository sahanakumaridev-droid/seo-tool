#!/usr/bin/env python3
"""Reassign featured images so no two pages share the same Unsplash photo."""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select
from db import AsyncSessionLocal, PageRecord
from services.image_service import normalize_image_key, reassign_unique_featured_images


async def main():
    async with AsyncSessionLocal() as s:
        rows = (await s.execute(select(PageRecord).order_by(PageRecord.created_at.asc()))).scalars().all()
        before = {}
        for r in rows:
            b = r.seo_block if isinstance(r.seo_block, dict) else {}
            k = normalize_image_key((b or {}).get("featured_image_url") or "")
            if k:
                before[k] = before.get(k, 0) + 1
        dupes = sum(1 for v in before.values() if v > 1)
        print(f"pages={len(rows)} unique_featured={len(before)} duplicate_keys={dupes}")
        updated = await reassign_unique_featured_images(rows)
        await s.commit()
        rows = (await s.execute(select(PageRecord))).scalars().all()
        after = {}
        for r in rows:
            b = r.seo_block if isinstance(r.seo_block, dict) else {}
            k = normalize_image_key((b or {}).get("featured_image_url") or "")
            if k:
                after[k] = after.get(k, 0) + 1
        dupes2 = sum(1 for v in after.values() if v > 1)
        print(f"updated={updated} unique_featured={len(after)} duplicate_keys={dupes2}")


if __name__ == "__main__":
    asyncio.run(main())
