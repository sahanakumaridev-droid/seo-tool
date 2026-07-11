from fastapi import APIRouter
from pydantic import BaseModel
from typing import List
import asyncio

from services.indexing_service import submit_url, is_configured

router = APIRouter()


class IndexRequest(BaseModel):
    urls: List[str]
    action: str = "URL_UPDATED"


@router.get("/status")
async def indexing_status():
    """Whether Google auto-indexing is configured (key present + auth OK)."""
    return {"configured": is_configured()}


@router.post("/submit")
async def indexing_submit(req: IndexRequest):
    """Submit one or more URLs to the Google Indexing API."""
    results = []
    for u in req.urls:
        res = await asyncio.to_thread(submit_url, u, req.action)
        results.append({"url": u, **res})
    ok = sum(1 for r in results if r.get("ok"))
    return {"submitted": ok, "total": len(results), "results": results}
