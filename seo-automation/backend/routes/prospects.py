"""Prospect lists for ZeOrbit outreach. Ready rows have both a public email and a phone."""
import json
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import delete as sa_delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from db import ProspectRecord, get_session
from services.prospect_list_service import search_prospects, socials_json

router = APIRouter()


class ProspectSearch(BaseModel):
    industry: str = Field(..., min_length=2, max_length=80)
    location: str = Field(..., min_length=2, max_length=120)
    limit: int = Field(default=10, ge=1, le=20)


def _row(rec: ProspectRecord) -> dict:
    try:
        socials = json.loads(rec.socials or "{}")
    except json.JSONDecodeError:
        socials = {}
    if not isinstance(socials, dict):
        socials = {}
    email = (rec.email or "").strip()
    phone = (rec.phone or "").strip()
    return {
        "id": rec.id,
        "place_id": rec.place_id or "",
        "business_name": rec.business_name or "",
        "website": rec.website or "",
        "category": rec.category or "",
        "address": rec.address or "",
        "city": rec.city or "",
        "state": rec.state or "",
        "zip_code": rec.zip_code or "",
        "phone": phone,
        "email": email,
        "maps_url": rec.maps_url or "",
        "rating": rec.rating,
        "review_count": rec.review_count,
        "socials": socials,
        "query": rec.query or "",
        "ready": bool(email and phone),
        "created_at": rec.created_at.isoformat() if rec.created_at else None,
    }


def _apply(rec: ProspectRecord, row: dict) -> None:
    rec.place_id = (row.get("place_id") or "")[:200]
    rec.business_name = (row.get("business_name") or "")[:200]
    rec.website = (row.get("website") or "")[:400]
    rec.category = (row.get("category") or "")[:160]
    rec.address = (row.get("address") or "")[:300]
    rec.city = (row.get("city") or "")[:80]
    rec.state = (row.get("state") or "")[:40]
    rec.zip_code = (row.get("zip_code") or "")[:20]
    rec.phone = (row.get("phone") or "")[:60]
    rec.email = (row.get("email") or "")[:200]
    rec.maps_url = (row.get("maps_url") or "")[:500]
    rec.rating = row.get("rating")
    rec.review_count = row.get("review_count")
    rec.socials = socials_json(row.get("socials"))
    rec.query = (row.get("query") or "")[:200]


@router.get("/")
async def list_prospects(ready_only: bool = False, session: AsyncSession = Depends(get_session)):
    rows = (await session.execute(select(ProspectRecord).order_by(ProspectRecord.id.desc()).limit(200))).scalars().all()
    payload = [_row(rec) for rec in rows]
    ready = sum(1 for item in payload if item["ready"])
    if ready_only:
        payload = [item for item in payload if item["ready"]]
    return {"prospects": payload, "total": len(rows), "ready": ready}


@router.post("/search")
async def run_search(req: ProspectSearch, session: AsyncSession = Depends(get_session)):
    try:
        found = await search_prospects(req.industry, req.location, req.limit)
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    saved: List[dict] = []
    for row in found:
        place_id = (row.get("place_id") or "").strip()
        existing = None
        if place_id:
            existing = (await session.execute(
                select(ProspectRecord).where(ProspectRecord.place_id == place_id)
            )).scalar_one_or_none()
        if existing is None and row.get("phone") and row.get("business_name"):
            existing = (await session.execute(
                select(ProspectRecord).where(
                    ProspectRecord.business_name == row["business_name"][:200],
                    ProspectRecord.phone == (row.get("phone") or "")[:60],
                )
            )).scalar_one_or_none()
        rec = existing or ProspectRecord()
        _apply(rec, row)
        if existing is None:
            session.add(rec)
        saved.append(rec)
    await session.commit()
    for rec in saved:
        await session.refresh(rec)
    payload = [_row(rec) for rec in saved]
    ready = [item for item in payload if item["ready"]]
    return {
        "discovered": len(payload),
        "ready": len(ready),
        "prospects": payload,
        "note": (
            "A prospect is ready for cold email only when both a public email and a phone number were found. "
            + (
                "This search used Google Business listings."
                if (settings.GOOGLE_PLACES_API_KEY or "").strip()
                else "This search used free OpenStreetMap listings."
            )
        ),
    }


@router.delete("/{prospect_id}")
async def delete_prospect(prospect_id: int, session: AsyncSession = Depends(get_session)):
    rec = (await session.execute(select(ProspectRecord).where(ProspectRecord.id == prospect_id))).scalar_one_or_none()
    if not rec:
        raise HTTPException(status_code=404, detail="Prospect not found")
    await session.execute(sa_delete(ProspectRecord).where(ProspectRecord.id == prospect_id))
    await session.commit()
    return {"deleted": True}
