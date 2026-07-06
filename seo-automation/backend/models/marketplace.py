"""
marketplace.py — Pydantic schemas for the Service Marketplace module
Covers: Users, Service Requests, Quotes, Messages, Credits, Reviews
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


# ── Enums ────────────────────────────────────────────────────────────────────

class UserRole(str, Enum):
    client       = "client"
    professional = "professional"
    admin        = "admin"


class RequestStatus(str, Enum):
    open      = "open"
    quoted    = "quoted"
    hired     = "hired"
    completed = "completed"
    cancelled = "cancelled"


class QuoteStatus(str, Enum):
    pending  = "pending"
    accepted = "accepted"
    rejected = "rejected"


class ServiceCategory(str, Enum):
    seo            = "SEO"
    web_dev        = "Web Development"
    marketing      = "Digital Marketing"
    content        = "Content Writing"
    social_media   = "Social Media"
    ppc            = "PPC / Ads"
    email_mktg     = "Email Marketing"
    graphic_design = "Graphic Design"
    video          = "Video Production"
    consulting     = "Business Consulting"
    other          = "Other"


# ── User Schemas ─────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    name: str = Field(..., min_length=2)
    role: UserRole = UserRole.client
    # Professional-only fields
    bio: Optional[str] = None
    skills: Optional[List[str]] = []
    hourly_rate: Optional[float] = None
    location: Optional[str] = None
    website: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserPublic(BaseModel):
    id: int
    email: str
    name: str
    role: UserRole
    bio: Optional[str] = None
    skills: List[str] = []
    hourly_rate: Optional[float] = None
    location: Optional[str] = None
    website: Optional[str] = None
    avatar_url: Optional[str] = None
    credits: int = 0
    rating: Optional[float] = None
    review_count: int = 0
    is_verified: bool = False
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    name: Optional[str] = None
    bio: Optional[str] = None
    skills: Optional[List[str]] = None
    hourly_rate: Optional[float] = None
    location: Optional[str] = None
    website: Optional[str] = None
    avatar_url: Optional[str] = None


class TokenOut(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserPublic


# ── Service Request Schemas ───────────────────────────────────────────────────

class ServiceRequestCreate(BaseModel):
    title: str = Field(..., min_length=5, max_length=200)
    description: str = Field(..., min_length=20)
    category: ServiceCategory
    budget_min: Optional[float] = None
    budget_max: Optional[float] = None
    location: Optional[str] = None          # e.g. "San Diego, CA"
    remote_ok: bool = True
    deadline: Optional[str] = None          # ISO date string
    skills_needed: List[str] = []


class ServiceRequestOut(BaseModel):
    id: int
    title: str
    description: str
    category: str
    budget_min: Optional[float] = None
    budget_max: Optional[float] = None
    location: Optional[str] = None
    remote_ok: bool = True
    deadline: Optional[str] = None
    skills_needed: List[str] = []
    status: RequestStatus = RequestStatus.open
    client_id: int
    client_name: str
    quote_count: int = 0
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ── Quote Schemas ─────────────────────────────────────────────────────────────

class QuoteCreate(BaseModel):
    request_id: int
    price: float = Field(..., gt=0)
    delivery_days: int = Field(..., gt=0)
    cover_letter: str = Field(..., min_length=20)


class QuoteOut(BaseModel):
    id: int
    request_id: int
    professional_id: int
    professional_name: str
    professional_rating: Optional[float] = None
    price: float
    delivery_days: int
    cover_letter: str
    status: QuoteStatus = QuoteStatus.pending
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ── Message Schemas ───────────────────────────────────────────────────────────

class MessageCreate(BaseModel):
    recipient_id: int
    content: str = Field(..., min_length=1)
    request_id: Optional[int] = None        # optional thread context


class MessageOut(BaseModel):
    id: int
    sender_id: int
    sender_name: str
    recipient_id: int
    content: str
    request_id: Optional[int] = None
    read: bool = False
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ── Review Schemas ────────────────────────────────────────────────────────────

class ReviewCreate(BaseModel):
    professional_id: int
    request_id: int
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None


class ReviewOut(BaseModel):
    id: int
    client_id: int
    client_name: str
    professional_id: int
    request_id: int
    rating: int
    comment: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ── Credit / Payment Schemas ──────────────────────────────────────────────────

class CreditPackage(BaseModel):
    id: str
    name: str
    credits: int
    price_usd: float
    description: str


class CreditPurchase(BaseModel):
    package_id: str
    # In production: add Stripe payment_intent_id here


class CreditTransaction(BaseModel):
    id: int
    user_id: int
    amount: int          # positive = purchase, negative = spend
    description: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ── Admin Schemas ─────────────────────────────────────────────────────────────

class AdminStats(BaseModel):
    total_users: int
    total_clients: int
    total_professionals: int
    total_requests: int
    open_requests: int
    total_quotes: int
    total_messages: int
    total_credits_sold: int
