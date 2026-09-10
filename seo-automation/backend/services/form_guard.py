"""Public contact-form checks: US phone numbers and low-quality/spam email."""
from __future__ import annotations

import re

_DISPOSABLE = frozenset({
    "mailinator.com", "guerrillamail.com", "guerrillamail.net", "sharklasers.com",
    "grr.la", "yopmail.com", "tempmail.com", "temp-mail.org", "throwawaymail.com",
    "10minutemail.com", "10minutemail.net", "trashmail.com", "trashmail.net",
    "fakeinbox.com", "getnada.com", "emailondeck.com", "moakt.com",
    "dispostable.com", "mailnesia.com", "maildrop.cc", "tempail.com",
    "discard.email", "mailcatch.com", "mytemp.email", "tmpmail.org",
    "inboxkitten.com", "spamgourmet.com", "mailnull.com", "spam4.me",
    "mintemail.com", "jetable.org", "kasmail.com", "spamspot.com",
    "trash-mail.com", "tempr.email", "tmpeml.com", "dropmail.me",
})

_PLACEHOLDER_DOMAINS = frozenset({
    "example.com", "example.org", "example.net", "test.com", "test.org",
    "mailinator.com",
})
_PLACEHOLDER_LOCAL = frozenset({"test", "demo", "fake", "asdf", "qwerty", "user", "sample", "noreply"})
_EMAIL_RE = re.compile(r"^[A-Z0-9._%+\-]+@[A-Z0-9.\-]+\.[A-Z]{2,}$", re.I)
_TLD_BLOCK = frozenset({"ru", "cn", "tk", "ml", "ga", "cf", "gq", "top", "zip", "mov", "xyz"})


def normalize_us_phone(raw: str) -> str:
    digits = re.sub(r"\D", "", raw or "")
    if digits.startswith("1") and len(digits) == 11:
        digits = digits[1:]
    return digits


def is_valid_us_phone(raw: str) -> bool:
    """NANP: 10 digits, area code and exchange cannot start with 0 or 1."""
    digits = normalize_us_phone(raw)
    if len(digits) != 10:
        return False
    if digits[0] in "01" or digits[3] in "01":
        return False
    if digits[3:6] == "555":
        return False
    return True


def format_us_phone(raw: str) -> str:
    digits = normalize_us_phone(raw)
    if len(digits) != 10:
        return (raw or "").strip()
    return f"+1 ({digits[0:3]}) {digits[3:6]}-{digits[6:10]}"


def email_reject_reason(raw: str) -> str:
    email = (raw or "").strip().lower()
    if not email or not _EMAIL_RE.match(email):
        return "Enter a valid email address."
    if ".." in email or email.startswith(".") or email.endswith("."):
        return "Enter a valid email address."
    domain = email.rsplit("@", 1)[-1]
    local = email.split("@", 1)[0]
    tld = domain.rsplit(".", 1)[-1] if "." in domain else domain
    if domain in _PLACEHOLDER_DOMAINS or domain in _DISPOSABLE or any(domain.endswith("." + d) for d in _DISPOSABLE):
        return "Please use a real business or personal email — test and temporary inboxes are not accepted."
    if local in _PLACEHOLDER_LOCAL:
        return "Please use a real email address, not a test or demo address."
    if tld in _TLD_BLOCK:
        return "Please use a valid U.S. or standard business email address."
    if re.fullmatch(r"[a-z0-9]{20,}", local) and sum(c.isdigit() for c in local) >= 8:
        return "Please use a valid email address."
    return ""


def is_usable_contact_email(raw: str) -> bool:
    return not email_reject_reason(raw or "")


def identifier_reject_reason(name: str, email: str, phone: str) -> str:
    """Lead-gen click capture: name OR valid email OR valid U.S. phone."""
    n = (name or "").strip()
    e = (email or "").strip()
    p = (phone or "").strip()
    name_ok = len(n) >= 2
    email_err = email_reject_reason(e) if e else ""
    email_ok = bool(e) and not email_err
    phone_ok = bool(p) and is_valid_us_phone(p)
    if e and email_err:
        return email_err
    if p and not is_valid_us_phone(p):
        return "Enter a valid U.S. phone number."
    if name_ok or email_ok or phone_ok:
        return ""
    return "Leave a name, email, or U.S. phone so we can follow up."
