"""Send website form inquiries to the ZeOrbit inbox."""
from __future__ import annotations

import logging
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr, parseaddr
from html import escape

from config import settings

logger = logging.getLogger(__name__)


def smtp_configured() -> bool:
    return bool(settings.SMTP_HOST and settings.LEAD_NOTIFY_TO)


def _clean(value: str | None) -> str:
    return (value or "").strip()


def _row(label: str, value: str) -> str:
    if not value:
        return ""
    return (
        f"<tr><td style='padding:8px 12px;color:#64748b;width:140px;vertical-align:top'>"
        f"{escape(label)}</td>"
        f"<td style='padding:8px 12px;color:#0b1220'>{escape(value)}</td></tr>"
    )


def notify_lead(lead: dict) -> None:
    """Email a new website inquiry. Never raises — form save must still succeed."""
    if not smtp_configured():
        logger.warning("Lead email skipped: SMTP_HOST / LEAD_NOTIFY_TO not set")
        return

    name = _clean(lead.get("name")) or _clean(lead.get("contact_name")) or "Website visitor"
    email = _clean(lead.get("email"))
    phone = _clean(lead.get("phone"))
    company = _clean(lead.get("business_name"))
    service = _clean(lead.get("service"))
    budget = _clean(lead.get("budget"))
    source = _clean(lead.get("source")) or "website"
    message = _clean(lead.get("message"))
    location = _clean(lead.get("location"))
    page = _clean(lead.get("website"))
    if page.startswith("http"):
        page_label = page
    else:
        page_label = ""

    subject = f"New ZeOrbit inquiry from {name}"
    if service:
        subject = f"New ZeOrbit inquiry — {service} — {name}"

    text_lines = [
        "A new inquiry was submitted on the ZeOrbit website.",
        "",
        f"Name: {name}",
        f"Email: {email or '—'}",
        f"Phone: {phone or '—'}",
        f"Company: {company or '—'}",
        f"Service: {service or '—'}",
        f"Budget: {budget or '—'}",
        f"Location: {location or '—'}",
        f"Source: {source}",
        f"Submitted from: {page_label or '—'}",
        "",
        "Message:",
        message or "—",
    ]
    text_body = "\n".join(text_lines)

    html_body = f"""<!DOCTYPE html>
<html><body style="margin:0;padding:24px;background:#f6f7f9;font-family:Manrope,Arial,sans-serif">
  <div style="max-width:640px;margin:0 auto;background:#fff;border-radius:16px;overflow:hidden;border:1px solid #e6e8ee">
    <div style="padding:20px 24px;background:#0b1220;color:#fff">
      <div style="font-size:12px;letter-spacing:.14em;text-transform:uppercase;opacity:.7">ZeOrbit website</div>
      <h1 style="margin:8px 0 0;font-size:22px">New inquiry</h1>
    </div>
    <table style="width:100%;border-collapse:collapse;font-size:15px;line-height:1.45">
      {_row("Name", name)}
      {_row("Email", email)}
      {_row("Phone", phone)}
      {_row("Company", company)}
      {_row("Service", service)}
      {_row("Budget", budget)}
      {_row("Location", location)}
      {_row("Source", source)}
      {_row("Submitted from", page_label)}
    </table>
    <div style="padding:16px 24px 24px">
      <div style="color:#64748b;font-size:12px;text-transform:uppercase;letter-spacing:.08em;margin-bottom:8px">Message</div>
      <div style="white-space:pre-wrap;color:#0b1220">{escape(message or "—")}</div>
    </div>
  </div>
</body></html>"""

    from_email = _clean(settings.SMTP_FROM) or _clean(settings.SMTP_USER) or settings.LEAD_NOTIFY_TO
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = formataddr(("ZeOrbit Website", from_email))
    msg["To"] = settings.LEAD_NOTIFY_TO
    if email and "@" in email:
        _, addr = parseaddr(email)
        if addr:
            msg["Reply-To"] = addr
    msg.attach(MIMEText(text_body, "plain", "utf-8"))
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    host = settings.SMTP_HOST
    port = int(settings.SMTP_PORT or 587)
    user = _clean(settings.SMTP_USER)
    password = settings.SMTP_PASSWORD or ""

    try:
        if port == 465:
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(host, port, timeout=20, context=context) as smtp:
                if user:
                    smtp.login(user, password)
                smtp.send_message(msg)
        else:
            with smtplib.SMTP(host, port, timeout=20) as smtp:
                smtp.ehlo()
                if settings.SMTP_STARTTLS:
                    context = ssl.create_default_context()
                    smtp.starttls(context=context)
                    smtp.ehlo()
                if user:
                    smtp.login(user, password)
                smtp.send_message(msg)
        logger.info("Lead email sent to %s", settings.LEAD_NOTIFY_TO)
    except Exception:
        logger.exception("Failed to email lead to %s", settings.LEAD_NOTIFY_TO)
