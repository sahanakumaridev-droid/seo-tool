from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete as sa_delete
from db import get_session, LeadRecord
from models.schemas import LeadCreate, ProspectRequest
from services.leads_service import fetch_bark_leads, fetch_thumbtack_leads, parse_webhook_lead
from services.prospecting_service import discover_businesses
from typing import List, Optional

router = APIRouter()

VALID_STATUS = {"new", "contacted", "qualified", "closed"}

# Columns we accept when persisting a normalized lead dict.
_FIELDS = ("source", "name", "business_name", "contact_name", "email", "phone",
           "website", "industry", "service", "location", "budget", "message", "status")


def _to_dict(rec: LeadRecord) -> dict:
    return {
        "id": rec.id, "source": rec.source, "name": rec.name,
        "business_name": rec.business_name, "contact_name": rec.contact_name,
        "email": rec.email, "phone": rec.phone, "website": rec.website,
        "industry": rec.industry, "service": rec.service, "location": rec.location,
        "budget": rec.budget, "message": rec.message, "status": rec.status,
        "created_at": rec.created_at.isoformat() if rec.created_at else None,
    }


def _record_from(data: dict) -> LeadRecord:
    clean = {k: (data.get(k) or "") for k in _FIELDS}
    if not clean.get("status"):
        clean["status"] = "new"
    return LeadRecord(**clean)


async def _persist_many(session: AsyncSession, leads: List[dict]) -> int:
    added = 0
    for lead in leads:
        session.add(_record_from(lead))
        added += 1
    await session.commit()
    return added


@router.post("/", response_model=dict)
async def create_lead(lead: LeadCreate, session: AsyncSession = Depends(get_session)):
    """Manually create a lead."""
    rec = _record_from({**lead.model_dump(), "status": "new"})
    session.add(rec)
    await session.commit()
    await session.refresh(rec)
    return _to_dict(rec)


@router.get("/", response_model=List[dict])
async def list_leads(
    status: str = "", source: str = "", skip: int = 0, limit: int = 50,
    session: AsyncSession = Depends(get_session),
):
    """List leads with optional filtering."""
    stmt = select(LeadRecord).order_by(LeadRecord.id.desc())
    if status:
        stmt = stmt.where(LeadRecord.status == status)
    if source:
        stmt = stmt.where(LeadRecord.source == source)
    stmt = stmt.offset(skip).limit(limit)
    rows = (await session.execute(stmt)).scalars().all()
    return [_to_dict(r) for r in rows]


@router.get("/stats")
async def lead_stats(session: AsyncSession = Depends(get_session)):
    """Return lead statistics."""
    total = (await session.execute(select(func.count(LeadRecord.id)))).scalar() or 0
    by_status, by_source = {}, {}
    for col, bucket in ((LeadRecord.status, by_status), (LeadRecord.source, by_source)):
        rows = await session.execute(select(col, func.count(LeadRecord.id)).group_by(col))
        for key, cnt in rows.all():
            bucket[key or "unknown"] = cnt
    return {"total": total, "by_status": by_status, "by_source": by_source}


@router.patch("/{lead_id}/status")
async def update_lead_status(lead_id: int, status: str, session: AsyncSession = Depends(get_session)):
    """Update lead status: new | contacted | qualified | closed."""
    if status not in VALID_STATUS:
        raise HTTPException(status_code=400, detail=f"Status must be one of: {VALID_STATUS}")
    rec = (await session.execute(select(LeadRecord).where(LeadRecord.id == lead_id))).scalar_one_or_none()
    if not rec:
        raise HTTPException(status_code=404, detail="Lead not found")
    rec.status = status
    await session.commit()
    return _to_dict(rec)


@router.delete("/{lead_id}")
async def delete_lead(lead_id: int, session: AsyncSession = Depends(get_session)):
    rec = (await session.execute(select(LeadRecord).where(LeadRecord.id == lead_id))).scalar_one_or_none()
    if not rec:
        raise HTTPException(status_code=404, detail="Lead not found")
    await session.execute(sa_delete(LeadRecord).where(LeadRecord.id == lead_id))
    await session.commit()
    return {"deleted": True}


@router.post("/prospect")
async def prospect_leads(req: ProspectRequest, session: AsyncSession = Depends(get_session)):
    """Discover new businesses (Google Places) matching industry + location and save them as leads."""
    found = await discover_businesses(req.industry, req.location, req.limit)
    if not found:
        raise HTTPException(
            status_code=502,
            detail="No businesses discovered. Set GOOGLE_PLACES_API_KEY in .env to enable prospecting.",
        )
    added = await _persist_many(session, found)
    return {"discovered": added, "source": "prospecting", "leads": found}


@router.post("/sync/bark")
async def sync_bark_leads(session: AsyncSession = Depends(get_session)):
    """Pull latest leads from Bark.com."""
    added = await _persist_many(session, await fetch_bark_leads())
    return {"synced": added, "source": "bark"}


@router.post("/sync/thumbtack")
async def sync_thumbtack_leads(session: AsyncSession = Depends(get_session)):
    """Pull latest leads from Thumbtack."""
    added = await _persist_many(session, await fetch_thumbtack_leads())
    return {"synced": added, "source": "thumbtack"}


@router.post("/webhook/{source}")
async def lead_webhook(source: str, request: Request, session: AsyncSession = Depends(get_session)):
    """Receive a webhook from Bark, Thumbtack, or any platform and persist it."""
    try:
        payload = await request.json()
    except Exception:
        payload = {}
    lead = parse_webhook_lead(payload, source)
    if not lead:
        raise HTTPException(status_code=400, detail="Could not parse lead payload")
    rec = _record_from(lead)
    session.add(rec)
    await session.commit()
    await session.refresh(rec)
    return {"received": True, "lead_id": rec.id}
