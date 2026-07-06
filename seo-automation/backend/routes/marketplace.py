"""
marketplace.py — Service Requests, Quotes, Messages, Reviews, Credits
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update
from db import get_session
from db_marketplace import (
    UserRecord, ServiceRequestRecord, QuoteRecord,
    MessageRecord, ReviewRecord, CreditTransactionRecord
)
from models.marketplace import (
    ServiceRequestCreate, ServiceRequestOut,
    QuoteCreate, QuoteOut,
    MessageCreate, MessageOut,
    ReviewCreate, ReviewOut,
    CreditPurchase, CreditTransaction,
    AdminStats,
    UserPublic,
)
from auth import get_current_active_user
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# ── Credit packages available for purchase ────────────────────────────────────
CREDIT_PACKAGES = [
    {"id": "starter",  "name": "Starter",    "credits": 10,  "price_usd": 9.99,  "description": "10 lead credits — great for trying the platform"},
    {"id": "growth",   "name": "Growth",     "credits": 30,  "price_usd": 24.99, "description": "30 lead credits — most popular"},
    {"id": "pro",      "name": "Pro",        "credits": 100, "price_usd": 69.99, "description": "100 lead credits — best value for active pros"},
    {"id": "agency",   "name": "Agency",     "credits": 300, "price_usd": 179.99,"description": "300 lead credits — for agencies and power users"},
]
CREDITS_PER_PACKAGE = {p["id"]: p["credits"] for p in CREDIT_PACKAGES}
LEAD_COST = 2   # credits to respond to a lead


# ── Helpers ───────────────────────────────────────────────────────────────────

async def _get_user(session: AsyncSession, user_id: int) -> UserRecord:
    result = await session.execute(select(UserRecord).where(UserRecord.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def _req_to_out(r: ServiceRequestRecord) -> ServiceRequestOut:
    return ServiceRequestOut(
        id=r.id,
        title=r.title,
        description=r.description,
        category=r.category,
        budget_min=r.budget_min,
        budget_max=r.budget_max,
        location=r.location,
        remote_ok=r.remote_ok,
        deadline=r.deadline,
        skills_needed=r.skills_needed or [],
        status=r.status,
        client_id=r.client_id,
        client_name=r.client.name if r.client else "Unknown",
        quote_count=r.quote_count,
        created_at=r.created_at,
    )


# ── Service Requests ──────────────────────────────────────────────────────────

@router.post("/requests", response_model=ServiceRequestOut, status_code=201)
async def create_request(
    req: ServiceRequestCreate,
    session: AsyncSession = Depends(get_session),
    current_user = Depends(get_current_active_user),
):
    """Client posts a new service request."""
    user = await _get_user(session, int(current_user.user_id))
    if user.role not in ("client", "admin"):
        raise HTTPException(status_code=403, detail="Only clients can post requests")

    record = ServiceRequestRecord(
        title=req.title,
        description=req.description,
        category=req.category.value,
        budget_min=req.budget_min,
        budget_max=req.budget_max,
        location=req.location,
        remote_ok=req.remote_ok,
        deadline=req.deadline,
        skills_needed=req.skills_needed,
        client_id=user.id,
    )
    session.add(record)
    await session.commit()
    await session.refresh(record)
    # eager-load client name
    await session.refresh(record, ["client"])
    logger.info(f"Service request created: {record.id} by user {user.id}")
    return _req_to_out(record)


@router.get("/requests", response_model=list[ServiceRequestOut])
async def list_requests(
    category: str = "",
    location: str = "",
    status: str = "open",
    skip: int = 0,
    limit: int = 20,
    session: AsyncSession = Depends(get_session),
):
    """Browse open service requests (public)."""
    q = select(ServiceRequestRecord)
    if status:
        q = q.where(ServiceRequestRecord.status == status)
    if category:
        q = q.where(ServiceRequestRecord.category == category)
    if location:
        q = q.where(ServiceRequestRecord.location.ilike(f"%{location}%"))
    q = q.order_by(ServiceRequestRecord.created_at.desc()).offset(skip).limit(limit)
    result = await session.execute(q)
    records = result.scalars().all()
    # load clients
    out = []
    for r in records:
        await session.refresh(r, ["client"])
        out.append(_req_to_out(r))
    return out


@router.get("/requests/my", response_model=list[ServiceRequestOut])
async def my_requests(
    session: AsyncSession = Depends(get_session),
    current_user = Depends(get_current_active_user),
):
    """Get current client's own requests."""
    q = (select(ServiceRequestRecord)
         .where(ServiceRequestRecord.client_id == int(current_user.user_id))
         .order_by(ServiceRequestRecord.created_at.desc()))
    result = await session.execute(q)
    records = result.scalars().all()
    out = []
    for r in records:
        await session.refresh(r, ["client"])
        out.append(_req_to_out(r))
    return out


@router.get("/requests/{request_id}", response_model=ServiceRequestOut)
async def get_request(request_id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(
        select(ServiceRequestRecord).where(ServiceRequestRecord.id == request_id)
    )
    r = result.scalar_one_or_none()
    if not r:
        raise HTTPException(status_code=404, detail="Request not found")
    await session.refresh(r, ["client"])
    return _req_to_out(r)


@router.patch("/requests/{request_id}/status")
async def update_request_status(
    request_id: int,
    new_status: str,
    session: AsyncSession = Depends(get_session),
    current_user = Depends(get_current_active_user),
):
    result = await session.execute(
        select(ServiceRequestRecord).where(ServiceRequestRecord.id == request_id)
    )
    r = result.scalar_one_or_none()
    if not r:
        raise HTTPException(status_code=404, detail="Request not found")
    if r.client_id != int(current_user.user_id) and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    r.status = new_status
    await session.commit()
    return {"id": request_id, "status": new_status}


# ── Quotes ────────────────────────────────────────────────────────────────────

@router.post("/quotes", response_model=QuoteOut, status_code=201)
async def submit_quote(
    req: QuoteCreate,
    session: AsyncSession = Depends(get_session),
    current_user = Depends(get_current_active_user),
):
    """Professional submits a quote (costs LEAD_COST credits)."""
    user = await _get_user(session, int(current_user.user_id))
    if user.role not in ("professional", "admin"):
        raise HTTPException(status_code=403, detail="Only professionals can submit quotes")

    # Check credits
    if user.credits < LEAD_COST:
        raise HTTPException(
            status_code=402,
            detail=f"Insufficient credits. You need {LEAD_COST} credits to respond to a lead."
        )

    # Check request exists and is open
    req_result = await session.execute(
        select(ServiceRequestRecord).where(ServiceRequestRecord.id == req.request_id)
    )
    service_req = req_result.scalar_one_or_none()
    if not service_req:
        raise HTTPException(status_code=404, detail="Service request not found")
    if service_req.status not in ("open", "quoted"):
        raise HTTPException(status_code=400, detail="This request is no longer accepting quotes")

    # Deduct credits
    user.credits -= LEAD_COST
    session.add(CreditTransactionRecord(
        user_id=user.id,
        amount=-LEAD_COST,
        description=f"Quote submitted for request #{req.request_id}",
    ))

    # Create quote
    quote = QuoteRecord(
        request_id=req.request_id,
        professional_id=user.id,
        price=req.price,
        delivery_days=req.delivery_days,
        cover_letter=req.cover_letter,
    )
    session.add(quote)

    # Update request quote count and status
    service_req.quote_count = (service_req.quote_count or 0) + 1
    if service_req.status == "open":
        service_req.status = "quoted"

    await session.commit()
    await session.refresh(quote)
    await session.refresh(quote, ["professional"])

    return QuoteOut(
        id=quote.id,
        request_id=quote.request_id,
        professional_id=quote.professional_id,
        professional_name=quote.professional.name,
        professional_rating=quote.professional.rating,
        price=quote.price,
        delivery_days=quote.delivery_days,
        cover_letter=quote.cover_letter,
        status=quote.status,
        created_at=quote.created_at,
    )


@router.get("/quotes/request/{request_id}", response_model=list[QuoteOut])
async def get_quotes_for_request(
    request_id: int,
    session: AsyncSession = Depends(get_session),
    current_user = Depends(get_current_active_user),
):
    """Get all quotes for a request (client who owns it, or admin)."""
    req_result = await session.execute(
        select(ServiceRequestRecord).where(ServiceRequestRecord.id == request_id)
    )
    service_req = req_result.scalar_one_or_none()
    if not service_req:
        raise HTTPException(status_code=404, detail="Request not found")
    if service_req.client_id != int(current_user.user_id) and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    result = await session.execute(
        select(QuoteRecord).where(QuoteRecord.request_id == request_id)
        .order_by(QuoteRecord.created_at.desc())
    )
    quotes = result.scalars().all()
    out = []
    for q in quotes:
        await session.refresh(q, ["professional"])
        out.append(QuoteOut(
            id=q.id,
            request_id=q.request_id,
            professional_id=q.professional_id,
            professional_name=q.professional.name,
            professional_rating=q.professional.rating,
            price=q.price,
            delivery_days=q.delivery_days,
            cover_letter=q.cover_letter,
            status=q.status,
            created_at=q.created_at,
        ))
    return out


@router.patch("/quotes/{quote_id}/accept")
async def accept_quote(
    quote_id: int,
    session: AsyncSession = Depends(get_session),
    current_user = Depends(get_current_active_user),
):
    """Client accepts a quote — marks request as hired."""
    result = await session.execute(select(QuoteRecord).where(QuoteRecord.id == quote_id))
    quote = result.scalar_one_or_none()
    if not quote:
        raise HTTPException(status_code=404, detail="Quote not found")

    req_result = await session.execute(
        select(ServiceRequestRecord).where(ServiceRequestRecord.id == quote.request_id)
    )
    service_req = req_result.scalar_one_or_none()
    if service_req.client_id != int(current_user.user_id):
        raise HTTPException(status_code=403, detail="Not authorized")

    quote.status = "accepted"
    service_req.status = "hired"

    # Reject all other quotes for this request
    await session.execute(
        update(QuoteRecord)
        .where(QuoteRecord.request_id == quote.request_id, QuoteRecord.id != quote_id)
        .values(status="rejected")
    )
    await session.commit()
    return {"message": "Quote accepted", "quote_id": quote_id}


# ── Messages ──────────────────────────────────────────────────────────────────

@router.post("/messages", response_model=MessageOut, status_code=201)
async def send_message(
    req: MessageCreate,
    session: AsyncSession = Depends(get_session),
    current_user = Depends(get_current_active_user),
):
    """Send a message to another user."""
    sender_id = int(current_user.user_id)
    msg = MessageRecord(
        sender_id=sender_id,
        recipient_id=req.recipient_id,
        content=req.content,
        request_id=req.request_id,
    )
    session.add(msg)
    await session.commit()
    await session.refresh(msg)
    await session.refresh(msg, ["sender"])
    return MessageOut(
        id=msg.id,
        sender_id=msg.sender_id,
        sender_name=msg.sender.name,
        recipient_id=msg.recipient_id,
        content=msg.content,
        request_id=msg.request_id,
        read=msg.read,
        created_at=msg.created_at,
    )


@router.get("/messages/inbox", response_model=list[MessageOut])
async def get_inbox(
    session: AsyncSession = Depends(get_session),
    current_user = Depends(get_current_active_user),
):
    """Get all messages received by current user."""
    result = await session.execute(
        select(MessageRecord)
        .where(MessageRecord.recipient_id == int(current_user.user_id))
        .order_by(MessageRecord.created_at.desc())
    )
    msgs = result.scalars().all()
    out = []
    for m in msgs:
        await session.refresh(m, ["sender"])
        out.append(MessageOut(
            id=m.id, sender_id=m.sender_id, sender_name=m.sender.name,
            recipient_id=m.recipient_id, content=m.content,
            request_id=m.request_id, read=m.read, created_at=m.created_at,
        ))
    return out


@router.patch("/messages/{message_id}/read")
async def mark_read(
    message_id: int,
    session: AsyncSession = Depends(get_session),
    current_user = Depends(get_current_active_user),
):
    result = await session.execute(select(MessageRecord).where(MessageRecord.id == message_id))
    msg = result.scalar_one_or_none()
    if not msg or msg.recipient_id != int(current_user.user_id):
        raise HTTPException(status_code=404, detail="Message not found")
    msg.read = True
    await session.commit()
    return {"message_id": message_id, "read": True}


# ── Reviews ───────────────────────────────────────────────────────────────────

@router.post("/reviews", response_model=ReviewOut, status_code=201)
async def create_review(
    req: ReviewCreate,
    session: AsyncSession = Depends(get_session),
    current_user = Depends(get_current_active_user),
):
    """Client leaves a review for a professional."""
    review = ReviewRecord(
        client_id=int(current_user.user_id),
        professional_id=req.professional_id,
        request_id=req.request_id,
        rating=req.rating,
        comment=req.comment,
    )
    session.add(review)

    # Update professional's average rating
    pro = await _get_user(session, req.professional_id)
    total = (pro.rating or 0) * pro.review_count + req.rating
    pro.review_count += 1
    pro.rating = round(total / pro.review_count, 2)

    await session.commit()
    await session.refresh(review)
    await session.refresh(review, ["client"])
    return ReviewOut(
        id=review.id,
        client_id=review.client_id,
        client_name=review.client.name,
        professional_id=review.professional_id,
        request_id=review.request_id,
        rating=review.rating,
        comment=review.comment,
        created_at=review.created_at,
    )


@router.get("/reviews/professional/{professional_id}", response_model=list[ReviewOut])
async def get_reviews(professional_id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(
        select(ReviewRecord).where(ReviewRecord.professional_id == professional_id)
        .order_by(ReviewRecord.created_at.desc())
    )
    reviews = result.scalars().all()
    out = []
    for r in reviews:
        await session.refresh(r, ["client"])
        out.append(ReviewOut(
            id=r.id, client_id=r.client_id, client_name=r.client.name,
            professional_id=r.professional_id, request_id=r.request_id,
            rating=r.rating, comment=r.comment, created_at=r.created_at,
        ))
    return out


# ── Credits ───────────────────────────────────────────────────────────────────

@router.get("/credits/packages")
async def get_packages():
    """List available credit packages."""
    return CREDIT_PACKAGES


@router.post("/credits/purchase")
async def purchase_credits(
    req: CreditPurchase,
    session: AsyncSession = Depends(get_session),
    current_user = Depends(get_current_active_user),
):
    """Purchase credits (mock — integrate Stripe in production)."""
    credits = CREDITS_PER_PACKAGE.get(req.package_id)
    if not credits:
        raise HTTPException(status_code=400, detail="Invalid package")

    user = await _get_user(session, int(current_user.user_id))
    user.credits += credits
    session.add(CreditTransactionRecord(
        user_id=user.id,
        amount=credits,
        description=f"Purchased {req.package_id} package ({credits} credits)",
    ))
    await session.commit()
    return {"credits_added": credits, "new_balance": user.credits}


@router.get("/credits/balance")
async def get_balance(
    session: AsyncSession = Depends(get_session),
    current_user = Depends(get_current_active_user),
):
    user = await _get_user(session, int(current_user.user_id))
    return {"credits": user.credits}


@router.get("/credits/history", response_model=list[CreditTransaction])
async def credit_history(
    session: AsyncSession = Depends(get_session),
    current_user = Depends(get_current_active_user),
):
    result = await session.execute(
        select(CreditTransactionRecord)
        .where(CreditTransactionRecord.user_id == int(current_user.user_id))
        .order_by(CreditTransactionRecord.created_at.desc())
        .limit(50)
    )
    txns = result.scalars().all()
    return [CreditTransaction(
        id=t.id, user_id=t.user_id, amount=t.amount,
        description=t.description, created_at=t.created_at,
    ) for t in txns]


# ── Admin ─────────────────────────────────────────────────────────────────────

@router.get("/admin/stats", response_model=AdminStats)
async def admin_stats(
    session: AsyncSession = Depends(get_session),
    current_user = Depends(get_current_active_user),
):
    """Platform-wide stats for admin."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin only")

    total_users       = (await session.execute(select(func.count(UserRecord.id)))).scalar()
    total_clients     = (await session.execute(select(func.count(UserRecord.id)).where(UserRecord.role == "client"))).scalar()
    total_pros        = (await session.execute(select(func.count(UserRecord.id)).where(UserRecord.role == "professional"))).scalar()
    total_requests    = (await session.execute(select(func.count(ServiceRequestRecord.id)))).scalar()
    open_requests     = (await session.execute(select(func.count(ServiceRequestRecord.id)).where(ServiceRequestRecord.status == "open"))).scalar()
    total_quotes      = (await session.execute(select(func.count(QuoteRecord.id)))).scalar()
    total_messages    = (await session.execute(select(func.count(MessageRecord.id)))).scalar()
    credits_sold_row  = await session.execute(
        select(func.sum(CreditTransactionRecord.amount))
        .where(CreditTransactionRecord.amount > 0)
    )
    credits_sold = credits_sold_row.scalar() or 0

    return AdminStats(
        total_users=total_users,
        total_clients=total_clients,
        total_professionals=total_pros,
        total_requests=total_requests,
        open_requests=open_requests,
        total_quotes=total_quotes,
        total_messages=total_messages,
        total_credits_sold=credits_sold,
    )


@router.get("/admin/users", response_model=list[UserPublic])
async def admin_list_users(
    skip: int = 0,
    limit: int = 50,
    session: AsyncSession = Depends(get_session),
    current_user = Depends(get_current_active_user),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    result = await session.execute(
        select(UserRecord).offset(skip).limit(limit)
    )
    users = result.scalars().all()
    from routes.marketplace_auth import _user_to_public
    return [_user_to_public(u) for u in users]


@router.patch("/admin/users/{user_id}/verify")
async def verify_professional(
    user_id: int,
    session: AsyncSession = Depends(get_session),
    current_user = Depends(get_current_active_user),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    user = await _get_user(session, user_id)
    user.is_verified = True
    await session.commit()
    return {"user_id": user_id, "is_verified": True}
