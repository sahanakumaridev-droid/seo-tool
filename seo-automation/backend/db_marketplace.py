"""
db_marketplace.py — SQLAlchemy ORM models for the Marketplace module.
These tables are created alongside the existing 'pages' table.
"""
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, JSON,
    ForeignKey, Text, Enum as SAEnum
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db import Base   # reuse the same Base / engine


# ── Users ─────────────────────────────────────────────────────────────────────

class UserRecord(Base):
    __tablename__ = "users"

    id           = Column(Integer, primary_key=True, autoincrement=True)
    email        = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    name         = Column(String(120), nullable=False)
    role         = Column(String(20), nullable=False, default="client")   # client | professional | admin
    bio          = Column(Text, nullable=True)
    skills       = Column(JSON, default=list)
    hourly_rate  = Column(Float, nullable=True)
    location     = Column(String(120), nullable=True)
    website      = Column(String(255), nullable=True)
    avatar_url   = Column(String(500), nullable=True)
    credits      = Column(Integer, default=0)
    rating       = Column(Float, nullable=True)
    review_count = Column(Integer, default=0)
    is_verified  = Column(Boolean, default=False)
    is_active    = Column(Boolean, default=True)
    created_at   = Column(DateTime(timezone=True), server_default=func.now())
    updated_at   = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    # Relationships
    requests     = relationship("ServiceRequestRecord", back_populates="client",
                                foreign_keys="ServiceRequestRecord.client_id")
    quotes       = relationship("QuoteRecord", back_populates="professional",
                                foreign_keys="QuoteRecord.professional_id")
    sent_messages    = relationship("MessageRecord", back_populates="sender",
                                    foreign_keys="MessageRecord.sender_id")
    received_messages = relationship("MessageRecord", back_populates="recipient",
                                     foreign_keys="MessageRecord.recipient_id")
    reviews_given    = relationship("ReviewRecord", back_populates="client",
                                    foreign_keys="ReviewRecord.client_id")
    reviews_received = relationship("ReviewRecord", back_populates="professional",
                                    foreign_keys="ReviewRecord.professional_id")
    credit_transactions = relationship("CreditTransactionRecord", back_populates="user")


# ── Service Requests ──────────────────────────────────────────────────────────

class ServiceRequestRecord(Base):
    __tablename__ = "service_requests"

    id            = Column(Integer, primary_key=True, autoincrement=True)
    title         = Column(String(200), nullable=False)
    description   = Column(Text, nullable=False)
    category      = Column(String(80), nullable=False, index=True)
    budget_min    = Column(Float, nullable=True)
    budget_max    = Column(Float, nullable=True)
    location      = Column(String(120), nullable=True, index=True)
    remote_ok     = Column(Boolean, default=True)
    deadline      = Column(String(30), nullable=True)
    skills_needed = Column(JSON, default=list)
    status        = Column(String(20), default="open", index=True)   # open|quoted|hired|completed|cancelled
    client_id     = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    quote_count   = Column(Integer, default=0)
    created_at    = Column(DateTime(timezone=True), server_default=func.now())
    updated_at    = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    client = relationship("UserRecord", back_populates="requests",
                          foreign_keys=[client_id])
    quotes = relationship("QuoteRecord", back_populates="request")


# ── Quotes ────────────────────────────────────────────────────────────────────

class QuoteRecord(Base):
    __tablename__ = "quotes"

    id              = Column(Integer, primary_key=True, autoincrement=True)
    request_id      = Column(Integer, ForeignKey("service_requests.id"), nullable=False, index=True)
    professional_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    price           = Column(Float, nullable=False)
    delivery_days   = Column(Integer, nullable=False)
    cover_letter    = Column(Text, nullable=False)
    status          = Column(String(20), default="pending")   # pending|accepted|rejected
    created_at      = Column(DateTime(timezone=True), server_default=func.now())

    request      = relationship("ServiceRequestRecord", back_populates="quotes")
    professional = relationship("UserRecord", back_populates="quotes",
                                foreign_keys=[professional_id])


# ── Messages ──────────────────────────────────────────────────────────────────

class MessageRecord(Base):
    __tablename__ = "messages"

    id           = Column(Integer, primary_key=True, autoincrement=True)
    sender_id    = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    recipient_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    content      = Column(Text, nullable=False)
    request_id   = Column(Integer, ForeignKey("service_requests.id"), nullable=True)
    read         = Column(Boolean, default=False)
    created_at   = Column(DateTime(timezone=True), server_default=func.now())

    sender    = relationship("UserRecord", back_populates="sent_messages",
                             foreign_keys=[sender_id])
    recipient = relationship("UserRecord", back_populates="received_messages",
                             foreign_keys=[recipient_id])


# ── Reviews ───────────────────────────────────────────────────────────────────

class ReviewRecord(Base):
    __tablename__ = "reviews"

    id              = Column(Integer, primary_key=True, autoincrement=True)
    client_id       = Column(Integer, ForeignKey("users.id"), nullable=False)
    professional_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    request_id      = Column(Integer, ForeignKey("service_requests.id"), nullable=False)
    rating          = Column(Integer, nullable=False)   # 1-5
    comment         = Column(Text, nullable=True)
    created_at      = Column(DateTime(timezone=True), server_default=func.now())

    client       = relationship("UserRecord", back_populates="reviews_given",
                                foreign_keys=[client_id])
    professional = relationship("UserRecord", back_populates="reviews_received",
                                foreign_keys=[professional_id])


# ── Credit Transactions ───────────────────────────────────────────────────────

class CreditTransactionRecord(Base):
    __tablename__ = "credit_transactions"

    id          = Column(Integer, primary_key=True, autoincrement=True)
    user_id     = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    amount      = Column(Integer, nullable=False)   # positive = add, negative = spend
    description = Column(String(255), nullable=False)
    created_at  = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("UserRecord", back_populates="credit_transactions")
