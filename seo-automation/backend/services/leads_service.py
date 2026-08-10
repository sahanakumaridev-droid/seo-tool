"""
leads_service.py
Lead capture helpers — webhook normalization for inbound lead payloads.
"""
from typing import Optional


def parse_webhook_lead(payload: dict, source: str) -> Optional[dict]:
    """Normalize an inbound webhook payload into a lead dict."""
    if not isinstance(payload, dict):
        return None
    return {
        "source": source or "webhook",
        "name": payload.get("name") or payload.get("customer_name") or "Unknown",
        "email": payload.get("email") or payload.get("customer_email") or "",
        "phone": payload.get("phone") or payload.get("customer_phone") or "",
        "service": payload.get("service") or payload.get("service_type") or "",
        "location": payload.get("location", "") if isinstance(payload.get("location"), str) else "",
        "budget": str(payload.get("budget") or ""),
        "message": payload.get("message") or payload.get("description") or "",
        "status": "new",
    }
