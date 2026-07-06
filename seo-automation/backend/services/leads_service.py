"""
leads_service.py
Lead capture and management from Bark.com, Thumbtack, and manual entry.
Note: Bark and Thumbtack don't have public APIs — this uses webhook/email parsing patterns.
"""
import httpx
from typing import List, Optional
from config import settings


async def fetch_bark_leads() -> List[dict]:
    """
    Fetch leads from Bark.com.
    Bark doesn't have a public API — this uses their partner webhook endpoint if configured.
    Set BARK_API_KEY in .env to enable.
    """
    if not settings.BARK_API_KEY:
        return []
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(
                "https://www.bark.com/api/v1/leads",
                headers={"Authorization": f"Bearer {settings.BARK_API_KEY}"},
            )
            if resp.status_code == 200:
                data = resp.json()
                leads = []
                for item in data.get("leads", []):
                    leads.append({
                        "source": "bark",
                        "name": item.get("customer_name", "Unknown"),
                        "email": item.get("customer_email", ""),
                        "phone": item.get("customer_phone", ""),
                        "service": item.get("service_type", ""),
                        "location": item.get("location", ""),
                        "budget": item.get("budget", ""),
                        "message": item.get("description", ""),
                        "status": "new",
                    })
                return leads
    except Exception as e:
        print(f"[Leads] Bark fetch error: {e}")
    return []


async def fetch_thumbtack_leads() -> List[dict]:
    """
    Fetch leads from Thumbtack.
    Uses Thumbtack's partner API if THUMBTACK_API_KEY is set.
    """
    if not settings.THUMBTACK_API_KEY:
        return []
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(
                "https://pro-api.thumbtack.com/v2/leads",
                headers={
                    "Authorization": f"Bearer {settings.THUMBTACK_API_KEY}",
                    "Content-Type": "application/json",
                },
            )
            if resp.status_code == 200:
                data = resp.json()
                leads = []
                for item in data.get("leads", []):
                    customer = item.get("customer", {})
                    leads.append({
                        "source": "thumbtack",
                        "name": customer.get("name", "Unknown"),
                        "email": customer.get("email", ""),
                        "phone": customer.get("phone", ""),
                        "service": item.get("category", {}).get("name", ""),
                        "location": item.get("location", {}).get("city", ""),
                        "budget": str(item.get("budget", {}).get("amount", "")),
                        "message": item.get("description", ""),
                        "status": "new",
                    })
                return leads
    except Exception as e:
        print(f"[Leads] Thumbtack fetch error: {e}")
    return []


def parse_webhook_lead(payload: dict, source: str) -> Optional[dict]:
    """
    Parse incoming webhook payload from Bark/Thumbtack/other platforms.
    Each platform sends different formats — this normalizes them.
    """
    if source == "bark":
        return {
            "source": "bark",
            "name": payload.get("customer_name") or payload.get("name", "Unknown"),
            "email": payload.get("customer_email") or payload.get("email", ""),
            "phone": payload.get("customer_phone") or payload.get("phone", ""),
            "service": payload.get("service_type") or payload.get("service", ""),
            "location": payload.get("location", ""),
            "budget": payload.get("budget", ""),
            "message": payload.get("description") or payload.get("message", ""),
            "status": "new",
        }
    elif source == "thumbtack":
        customer = payload.get("customer", {})
        return {
            "source": "thumbtack",
            "name": customer.get("name", payload.get("name", "Unknown")),
            "email": customer.get("email", payload.get("email", "")),
            "phone": customer.get("phone", payload.get("phone", "")),
            "service": payload.get("category", {}).get("name", payload.get("service", "")),
            "location": payload.get("location", {}).get("city", payload.get("location", "")),
            "budget": str(payload.get("budget", {}).get("amount", payload.get("budget", ""))),
            "message": payload.get("description", payload.get("message", "")),
            "status": "new",
        }
    else:
        # Generic webhook format
        return {
            "source": source,
            "name": payload.get("name", "Unknown"),
            "email": payload.get("email", ""),
            "phone": payload.get("phone", ""),
            "service": payload.get("service", ""),
            "location": payload.get("location", ""),
            "budget": payload.get("budget", ""),
            "message": payload.get("message", ""),
            "status": "new",
        }
