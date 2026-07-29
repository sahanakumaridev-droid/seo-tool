"""
db_sqlite.py — SQLite fallback for Replit/demo deployments
Swap this in by setting DATABASE_URL=sqlite+aiosqlite:///./seo.db
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, Integer, String, DateTime, JSON, Boolean
from sqlalchemy.sql import func
from config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

class PageRecord(Base):
    __tablename__ = "pages"
    id            = Column(Integer, primary_key=True, autoincrement=True)
    business_type = Column(String(120), nullable=False, index=True)
    base_location = Column(String(120), nullable=False)
    city          = Column(String(80), nullable=False, index=True)
    state         = Column(String(10), nullable=False)
    slug          = Column(String(200), nullable=False, unique=True, index=True)
    seo_block     = Column(JSON, nullable=False)
    created_at    = Column(DateTime(timezone=True), server_default=func.now())
    updated_at    = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

class LeadRecord(Base):
    __tablename__ = "leads"
    id            = Column(Integer, primary_key=True, autoincrement=True)
    source        = Column(String(40), nullable=False, index=True)
    name          = Column(String(160), default="")
    business_name = Column(String(200), default="")
    contact_name  = Column(String(160), default="")
    email         = Column(String(200), default="")
    phone         = Column(String(60), default="")
    website       = Column(String(300), default="")
    industry      = Column(String(120), default="")
    service       = Column(String(160), default="")
    location      = Column(String(160), default="")
    budget        = Column(String(80), default="")
    message       = Column(String(2000), default="")
    status        = Column(String(20), default="new", index=True)
    created_at    = Column(DateTime(timezone=True), server_default=func.now())

class PublishedUrlRecord(Base):
    __tablename__ = "published_urls"
    id                  = Column(Integer, primary_key=True, autoincrement=True)
    url                 = Column(String(500), nullable=False, unique=True, index=True)
    source              = Column(String(40), nullable=False, default="wordpress", index=True)
    post_id             = Column(String(60), default="")
    title               = Column(String(300), default="")
    status              = Column(String(20), nullable=False, default="published", index=True)
    http_status         = Column(Integer, nullable=True)
    robots_allowed      = Column(Boolean, nullable=True)
    has_noindex         = Column(Boolean, nullable=True)
    canonical_ok        = Column(Boolean, nullable=True)
    coverage_state      = Column(String(200), default="")
    error_message       = Column(String(500), default="")
    sitemap_submitted_at = Column(DateTime(timezone=True), nullable=True)
    last_inspected_at   = Column(DateTime(timezone=True), nullable=True)
    created_at          = Column(DateTime(timezone=True), server_default=func.now())
    updated_at          = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("SQLite tables ready.")

async def get_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session
