"""
db.py — PostgreSQL via SQLAlchemy (async) + asyncpg
Tables:
  pages  — stores generated SEO pages as JSONB
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.sql import func
from config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

class PageRecord(Base):
    __tablename__ = "pages"

    id           = Column(Integer, primary_key=True, autoincrement=True)
    business_type = Column(String(120), nullable=False, index=True)
    base_location = Column(String(120), nullable=False)
    city         = Column(String(80), nullable=False, index=True)
    state        = Column(String(10), nullable=False)
    slug         = Column(String(200), nullable=False, unique=True, index=True)
    seo_block    = Column(JSON, nullable=False)          # full SEOBlock as JSON
    created_at   = Column(DateTime(timezone=True), server_default=func.now())
    updated_at   = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

async def init_db():
    """Create tables if they don't exist."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("PostgreSQL tables ready.")

async def get_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session
