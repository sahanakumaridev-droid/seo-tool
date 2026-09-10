"""First-party visitor intel from a pageview — no name/email guessing."""
from __future__ import annotations

import ipaddress
import json
from urllib.parse import urlparse, parse_qs


def _ua_device(ua: str) -> tuple[str, str]:
    u = (ua or "").lower()
    if "ipad" in u or ("android" in u and "mobile" not in u):
        device = "Tablet"
    elif "mobile" in u or "iphone" in u or "android" in u:
        device = "Phone"
    else:
        device = "Desktop"
    if "edg/" in u or "edg " in u:
        browser = "Edge"
    elif "chrome" in u and "chromium" not in u and "edg" not in u:
        browser = "Chrome"
    elif "firefox" in u:
        browser = "Firefox"
    elif "safari" in u and "chrome" not in u:
        browser = "Safari"
    elif "cursor" in u:
        browser = "Cursor"
    else:
        browser = "Browser"
    return device, browser


def _referrer_label(referrer: str, path: str) -> str:
    raw = (referrer or "").strip()
    if not raw:
        qs = parse_qs(urlparse(path).query)
        src = (qs.get("utm_source") or [""])[0]
        if src:
            return f"Campaign · {src}"[:80]
        return "Direct"
    host = (urlparse(raw).hostname or "").lower().replace("www.", "")
    if not host:
        return "Direct"
    if "google." in host:
        return "Google"
    if "bing." in host:
        return "Bing"
    if host in {"facebook.com", "m.facebook.com", "l.facebook.com"}:
        return "Facebook"
    if "instagram" in host:
        return "Instagram"
    if "linkedin" in host:
        return "LinkedIn"
    if host in {"localhost", "127.0.0.1"}:
        return "Same site"
    return host[:80]


def _place_from_ip(ip: str, country_header: str, timezone: str) -> str:
    tz = (timezone or "").strip()
    cc = (country_header or "").strip().upper()
    try:
        addr = ipaddress.ip_address((ip or "").split("%")[0])
        if addr.is_private or addr.is_loopback:
            if tz:
                return f"Local · {tz}"
            return "Local computer"
    except ValueError:
        pass
    bits = []
    if cc and cc not in {"XX", "T1"}:
        bits.append(cc)
    if tz:
        bits.append(tz)
    if ip:
        bits.append(ip)
    return " · ".join(bits)[:160] if bits else "Unknown"


def enrich_visit(payload: dict, request) -> dict:
    path = str(payload.get("path") or payload.get("page_url") or "/")[:300]
    referrer = str(payload.get("referrer") or "")[:400]
    session_id = str(payload.get("session_id") or "")[:64]
    language = str(payload.get("language") or request.headers.get("accept-language") or "")[:40]
    timezone = str(payload.get("timezone") or "")[:60]
    screen = str(payload.get("screen") or "")[:20]
    ua = (request.headers.get("user-agent") or str(payload.get("user_agent") or ""))[:240]
    forwarded = (request.headers.get("x-forwarded-for") or "").split(",")[0].strip()
    ip = forwarded or (request.client.host if request.client else "") or "unknown"
    country = request.headers.get("cf-ipcountry") or request.headers.get("x-country") or ""
    device, browser = _ua_device(ua)
    source_label = _referrer_label(referrer, path)
    extra = json.dumps(
        {
            "tz": timezone,
            "lang": language,
            "screen": screen,
            "ref": referrer[:200],
            "ua": ua[:180],
            "title": str(payload.get("title") or "")[:160],
        },
        separators=(",", ":"),
    )[:2000]
    return {
        "source": "pageview",
        "name": f"{browser} · {device}",
        "contact_name": source_label,
        "email": "",
        "phone": "",
        "website": path or "/",
        "industry": session_id,
        "service": device,
        "location": _place_from_ip(ip, country, timezone),
        "budget": browser,
        "message": extra,
        "status": "new",
    }


def visitor_card(row: dict) -> dict:
    """Fill device/referrer/locale for UI, including older skinny pageviews."""
    d = dict(row)
    msg = d.get("message") or ""
    extra = {}
    ua = ""
    ref = ""
    if msg.startswith("{"):
        try:
            extra = json.loads(msg)
        except Exception:
            extra = {}
        ua = str(extra.get("ua") or "")
        ref = str(extra.get("ref") or "")
    else:
        for line in msg.splitlines():
            if line.startswith("ua="):
                ua = line[3:]
            elif line.startswith("referrer="):
                ref = line[9:]
    if (d.get("name") or "") in ("", "Anonymous visitor", "Visitor"):
        device, browser = _ua_device(ua)
        d["name"] = f"{browser} · {device}"
        d["service"] = d.get("service") or device
        d["budget"] = d.get("budget") or browser
    if not d.get("contact_name"):
        d["contact_name"] = _referrer_label(ref, d.get("website") or "/")
    loc = d.get("location") or ""
    if loc in ("127.0.0.1", "localhost", "::1"):
        tz = extra.get("tz") or ""
        d["location"] = f"Local · {tz}" if tz else "Local computer"
    d["language"] = extra.get("lang") or ""
    d["screen"] = extra.get("screen") or ""
    d["timezone"] = extra.get("tz") or ""
    d["referrer"] = extra.get("ref") or ref or d.get("contact_name") or ""
    d["page_title"] = extra.get("title") or ""
    return d
