from fastapi import APIRouter, HTTPException
from db import get_db
from models.schemas import SEOPage, SEOBlock
from services.content_service import generate_seo_block
from datetime import datetime
from typing import List
import re

router = APIRouter()

def slugify(text: str) -> str:
    return re.sub(r'[^a-z0-9-]', '', text.lower().replace(' ', '-'))

@router.post("/save", response_model=dict)
async def save_page(business_type: str, city: str, state: str = "CA"):
    db = get_db()
    block = await generate_seo_block(business_type, city, state)
    slug = slugify(f"{business_type}-{city}")
    doc = {
        "business_type": business_type,
        "base_location": f"{city}, {state}",
        "city": city,
        "state": state,
        "slug": slug,
        "seo_block": block.model_dump(),
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
    result = await db.pages.replace_one({"slug": slug}, doc, upsert=True)
    return {"slug": slug, "saved": True}

@router.get("/", response_model=List[dict])
async def list_pages(skip: int = 0, limit: int = 20):
    db = get_db()
    cursor = db.pages.find({}, {"_id": 0}).skip(skip).limit(limit)
    return await cursor.to_list(length=limit)

@router.get("/{slug}", response_model=dict)
async def get_page(slug: str):
    db = get_db()
    page = await db.pages.find_one({"slug": slug}, {"_id": 0})
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")
    return page

@router.delete("/{slug}")
async def delete_page(slug: str):
    db = get_db()
    result = await db.pages.delete_one({"slug": slug})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Page not found")
    return {"deleted": True}
