"""Self-hosted contact-form captcha — no Google keys required."""
from __future__ import annotations

import secrets
import time
import random
from collections import defaultdict, deque
from threading import Lock
from urllib.parse import quote
from hmac import compare_digest

ALPHABET = "ACDEFGHJKMNPQRTUVWXY2346789"
CODE_LEN = 5
TTL_SECONDS = 10 * 60
MAX_ATTEMPTS = 5
MAX_LIVE = 4000
MIN_FILL_MS = 2500
RATE_WINDOW_S = 15 * 60
RATE_MAX = 8
_SKIP_CAPTCHA = frozenset({"manual", "prospecting", "instant-quote"})


def is_public_source(source: str) -> bool:
    return (source or "").strip().lower() not in _SKIP_CAPTCHA

_lock = Lock()
_challenges: dict[str, dict] = {}
_hits: dict[str, deque] = defaultdict(deque)


def _purge_locked(now: float) -> None:
    expired = [cid for cid, row in _challenges.items() if row["exp"] < now]
    for cid in expired:
        _challenges.pop(cid, None)


def issue() -> dict:
    code = "".join(secrets.choice(ALPHABET) for _ in range(CODE_LEN))
    cid = secrets.token_urlsafe(16)
    now = time.time()
    with _lock:
        _purge_locked(now)
        if len(_challenges) >= MAX_LIVE:
            oldest = min(_challenges, key=lambda k: _challenges[k]["exp"])
            _challenges.pop(oldest, None)
        _challenges[cid] = {"code": code, "exp": now + TTL_SECONDS, "tries": 0}
    svg = _svg(code)
    return {
        "id": cid,
        "image": "data:image/svg+xml;charset=utf-8," + quote(svg),
    }


def verify(cid: str, answer: str) -> bool:
    token = (cid or "").strip()
    guess = "".join((answer or "").split()).upper()
    if not token or len(guess) != CODE_LEN:
        return False
    now = time.time()
    with _lock:
        _purge_locked(now)
        row = _challenges.get(token)
        if not row:
            return False
        row["tries"] += 1
        ok = compare_digest(row["code"], guess)
        if ok or row["tries"] >= MAX_ATTEMPTS:
            _challenges.pop(token, None)
        return ok


def too_fast(started_at_ms: int) -> bool:
    if not started_at_ms:
        return True
    try:
        elapsed = int(time.time() * 1000) - int(started_at_ms)
    except (TypeError, ValueError):
        return True
    return elapsed < MIN_FILL_MS


def rate_limited(ip: str) -> bool:
    now = time.time()
    key = ip or "unknown"
    with _lock:
        q = _hits[key]
        while q and now - q[0] > RATE_WINDOW_S:
            q.popleft()
        if len(q) >= RATE_MAX:
            return True
        q.append(now)
        return False


def honeypot_tripped(value: str) -> bool:
    return bool((value or "").strip())


def _svg(code: str) -> str:
    rng = random.Random(code)
    width, height = 188, 58
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" rx="10" fill="#0b1220"/>',
    ]
    for _ in range(7):
        x1, y1 = rng.randint(6, 182), rng.randint(6, 52)
        x2, y2 = rng.randint(6, 182), rng.randint(6, 52)
        color = rng.choice(("#ff5a4e", "#64748b", "#3d8bff"))
        op = rng.choice(("0.16", "0.24", "0.32"))
        parts.append(
            f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" '
            f'stroke-opacity="{op}" stroke-width="1.15"/>'
        )
    for i, ch in enumerate(code):
        x = 16 + i * 34
        y = 38 + rng.randint(-5, 6)
        rot = rng.randint(-16, 16)
        size = rng.randint(22, 28)
        parts.append(
            f'<text x="{x}" y="{y}" fill="#f8fafc" font-family="ui-monospace, Menlo, monospace" '
            f'font-size="{size}" font-weight="700" transform="rotate({rot} {x} {y})">{ch}</text>'
        )
    parts.append("</svg>")
    return "".join(parts)
