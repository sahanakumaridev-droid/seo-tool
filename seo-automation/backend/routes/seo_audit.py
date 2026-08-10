from fastapi import APIRouter
from pydantic import BaseModel, Field

from models.schemas import AuditResult
from providers.real_site_audit import RealSiteAuditProvider

router = APIRouter()
_provider = RealSiteAuditProvider()


class AuditRequest(BaseModel):
    url: str = Field(..., example="https://example.com")


@router.post("/run", response_model=AuditResult)
async def run_audit(payload: AuditRequest):
    return await _provider.run_audit(payload.url)
