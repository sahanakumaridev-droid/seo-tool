"""Keep each login's posts separate. Existing rows stay with the admin account."""

from sqlalchemy import or_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from db import PageRecord


def normalize_owner(email: str | None) -> str:
    value = (email or "").strip().lower()
    if value in ("", "admin", "admin@zeorbit.com"):
        return "admin"
    return value


def row_owner(row) -> str:
    return normalize_owner(getattr(row, "owner_email", None))


def owner_clause(email: str | None):
    if not (email or "").strip():
        return PageRecord.id == -1
    owner = normalize_owner(email)
    if owner == "admin":
        return or_(
            PageRecord.owner_email.is_(None),
            func.lower(PageRecord.owner_email).in_(["", "admin", "admin@zeorbit.com"]),
        )
    return func.lower(PageRecord.owner_email) == owner


async def claim_slug(session: AsyncSession, slug: str, email: str | None):
    """Return a slug this account may write. Never overwrite another account's post."""
    owner = normalize_owner(email)
    result = await session.execute(select(PageRecord).where(PageRecord.slug == slug))
    existing = result.scalar_one_or_none()
    if existing is not None and row_owner(existing) != owner:
        suffix = owner.split("@")[0][:16] or "user"
        slug = f"{slug[:170].rstrip('-')}-{suffix}"
        result = await session.execute(select(PageRecord).where(PageRecord.slug == slug))
        existing = result.scalar_one_or_none()
    return slug, existing, owner
