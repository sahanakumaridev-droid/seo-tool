import asyncio
from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete as sa_delete
from db import get_session, LeadRecord
from models.schemas import LeadCreate, ProspectRequest
from services.leads_service import parse_webhook_lead
from services.prospecting_service import discover_businesses
from services.email_service import notify_lead
from services import captcha_service
from services import form_guard
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


def _client_ip(request: Request) -> str:
    forwarded = (request.headers.get("x-forwarded-for") or "").split(",")[0].strip()
    if forwarded:
        return forwarded
    if request.client and request.client.host:
        return request.client.host
    return "unknown"


@router.get("/captcha")
async def issue_captcha():
    """One-time visual challenge for public contact forms."""
    return captcha_service.issue()


@router.post("/", response_model=dict)
async def create_lead(lead: LeadCreate, request: Request, session: AsyncSession = Depends(get_session)):
    """Manually create a lead and email it to the ZeOrbit inbox."""
    public = captcha_service.is_public_source(lead.source)

    if public:
        if captcha_service.honeypot_tripped(lead.website_url):
            return {"id": 0, "status": "new", "source": lead.source}
        if captcha_service.rate_limited(_client_ip(request)):
            raise HTTPException(status_code=429, detail="Too many submissions. Please try again later.")
        if captcha_service.too_fast(lead.started_at):
            raise HTTPException(status_code=400, detail="Please complete the form and captcha, then send.")
        email_err = form_guard.email_reject_reason(lead.email or "")
        if email_err:
            raise HTTPException(status_code=400, detail=email_err)
        if not form_guard.is_valid_us_phone(lead.phone or ""):
            raise HTTPException(status_code=400, detail="Enter a valid U.S. phone number.")
        if not captcha_service.verify(lead.captcha_id, lead.captcha_answer):
            raise HTTPException(status_code=400, detail="Captcha is incorrect. Refresh the code and try again.")

    data = lead.model_dump()
    page_url = (data.pop("page_url", None) or "").strip()
    if page_url.startswith("https://") or page_url.startswith("http://"):
        data["website"] = page_url[:300]
    if public and data.get("phone"):
        data["phone"] = form_guard.format_us_phone(data["phone"])
    rec = _record_from({**data, "status": "new"})
    session.add(rec)
    await session.commit()
    await session.refresh(rec)
    payload = _to_dict(rec)
    await asyncio.to_thread(notify_lead, payload)
    return payload


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


@router.post("/webhook/{source}")
async def lead_webhook(source: str, request: Request, session: AsyncSession = Depends(get_session)):
    """Receive a webhook from any platform and persist it."""
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
    saved = _to_dict(rec)
    src = (lead.get("source") or source or "").lower()
    if src.startswith(("landing", "contact", "website")):
        await asyncio.to_thread(notify_lead, saved)
    return {"received": True, "lead_id": rec.id}
