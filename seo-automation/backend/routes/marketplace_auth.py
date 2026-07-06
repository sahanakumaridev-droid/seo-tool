"""
marketplace_auth.py — Full user registration / login with DB persistence.
Replaces the in-memory _users dict from the original auth.py.
"""
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db import get_session
from db_marketplace import UserRecord
from models.marketplace import UserCreate, UserLogin, UserPublic, TokenOut, UserUpdate
from auth import hash_password, verify_password, create_access_token, create_refresh_token
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


def _user_to_public(u: UserRecord) -> UserPublic:
    return UserPublic(
        id=u.id,
        email=u.email,
        name=u.name,
        role=u.role,
        bio=u.bio,
        skills=u.skills or [],
        hourly_rate=u.hourly_rate,
        location=u.location,
        website=u.website,
        avatar_url=u.avatar_url,
        credits=u.credits,
        rating=u.rating,
        review_count=u.review_count,
        is_verified=u.is_verified,
        created_at=u.created_at,
    )


@router.post("/register", response_model=TokenOut, status_code=201)
async def register(req: UserCreate, session: AsyncSession = Depends(get_session)):
    """Register a new user (client or professional)."""
    result = await session.execute(select(UserRecord).where(UserRecord.email == req.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    user = UserRecord(
        email=req.email,
        password_hash=hash_password(req.password),
        name=req.name,
        role=req.role.value,
        bio=req.bio,
        skills=req.skills or [],
        hourly_rate=req.hourly_rate,
        location=req.location,
        website=req.website,
        credits=10,   # welcome credits
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)

    access_token  = create_access_token(str(user.id), user.email)
    refresh_token = create_refresh_token(str(user.id), user.email)
    logger.info(f"New user registered: {user.email} role={user.role}")
    return TokenOut(access_token=access_token, refresh_token=refresh_token, user=_user_to_public(user))


@router.post("/login", response_model=TokenOut)
async def login(req: UserLogin, session: AsyncSession = Depends(get_session)):
    """Login with email + password."""
    result = await session.execute(select(UserRecord).where(UserRecord.email == req.email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is inactive")

    access_token  = create_access_token(str(user.id), user.email)
    refresh_token = create_refresh_token(str(user.id), user.email)
    logger.info(f"User logged in: {user.email}")
    return TokenOut(access_token=access_token, refresh_token=refresh_token, user=_user_to_public(user))


@router.get("/me", response_model=UserPublic)
async def get_me(
    session: AsyncSession = Depends(get_session),
    token_data = Depends(__import__("auth").get_current_active_user),
):
    """Get current user profile."""
    result = await session.execute(
        select(UserRecord).where(UserRecord.id == int(token_data.user_id))
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return _user_to_public(user)


@router.patch("/me", response_model=UserPublic)
async def update_me(
    req: UserUpdate,
    session: AsyncSession = Depends(get_session),
    token_data = Depends(__import__("auth").get_current_active_user),
):
    """Update current user profile."""
    result = await session.execute(
        select(UserRecord).where(UserRecord.id == int(token_data.user_id))
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    for field, value in req.model_dump(exclude_none=True).items():
        setattr(user, field, value)

    await session.commit()
    await session.refresh(user)
    return _user_to_public(user)


@router.get("/professionals", response_model=list[UserPublic])
async def list_professionals(
    category: str = "",
    location: str = "",
    skip: int = 0,
    limit: int = 20,
    session: AsyncSession = Depends(get_session),
):
    """Browse verified professionals."""
    q = select(UserRecord).where(UserRecord.role == "professional", UserRecord.is_active == True)
    if location:
        q = q.where(UserRecord.location.ilike(f"%{location}%"))
    q = q.offset(skip).limit(limit)
    result = await session.execute(q)
    users = result.scalars().all()
    return [_user_to_public(u) for u in users]
