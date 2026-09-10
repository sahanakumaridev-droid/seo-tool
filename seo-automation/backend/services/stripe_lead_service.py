"""Stripe Checkout → lead email. Email exists only after they type it on Stripe."""
from __future__ import annotations

import hmac
import hashlib
import logging
import time

import httpx

from config import settings

logger = logging.getLogger(__name__)
_API = "https://api.stripe.com/v1"


def stripe_configured() -> bool:
    return bool(settings.STRIPE_SECRET_KEY)


def _auth() -> tuple[str, str]:
    return (settings.STRIPE_SECRET_KEY, "")


def create_checkout_url(success_url: str = "", cancel_url: str = "") -> dict:
    if not stripe_configured():
        return {"ok": False, "detail": "Add STRIPE_SECRET_KEY in backend .env to use Stripe Checkout."}
    data = {
        "mode": "setup",
        "success_url": success_url or settings.STRIPE_SUCCESS_URL,
        "cancel_url": cancel_url or settings.STRIPE_CANCEL_URL,
        "billing_address_collection": "auto",
        "phone_number_collection[enabled]": "true",
        "customer_creation": "always",
    }
    try:
        with httpx.Client(timeout=20) as client:
            resp = client.post(f"{_API}/checkout/sessions", data=data, auth=_auth())
        body = resp.json()
        if resp.status_code >= 400:
            return {"ok": False, "detail": body.get("error", {}).get("message") or resp.text[:200]}
        return {"ok": True, "url": body.get("url"), "id": body.get("id")}
    except Exception as exc:
        logger.exception("Stripe checkout create failed")
        return {"ok": False, "detail": str(exc)[:200]}


def verify_webhook(payload: bytes, sig_header: str) -> bool:
    secret = settings.STRIPE_WEBHOOK_SECRET
    if not secret:
        return False
    parts = {}
    for item in (sig_header or "").split(","):
        if "=" in item:
            k, v = item.split("=", 1)
            parts.setdefault(k.strip(), []).append(v.strip())
    timestamp = (parts.get("t") or [""])[0]
    v1 = (parts.get("v1") or [""])[0]
    if not timestamp or not v1:
        return False
    try:
        if abs(time.time() - int(timestamp)) > 300:
            return False
    except ValueError:
        return False
    signed = f"{timestamp}.".encode() + payload
    expect = hmac.new(secret.encode(), signed, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expect, v1)


def lead_from_session(session: dict) -> dict | None:
    details = session.get("customer_details") or {}
    email = (details.get("email") or session.get("customer_email") or "").strip()
    name = (details.get("name") or "").strip()
    phone = (details.get("phone") or "").strip()
    if not email and not phone and not name:
        return None
    return {
        "source": "stripe",
        "name": name or email.split("@")[0],
        "contact_name": name,
        "email": email,
        "phone": phone,
        "service": "Stripe Checkout",
        "message": f"Stripe session {session.get('id') or ''}",
        "status": "new",
    }
