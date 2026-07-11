"""
indexing_service.py — submits URLs to the Google Indexing API so newly
published pages get crawled fast.

Requires GOOGLE_INDEXING_KEY_FILE (a service-account JSON key) whose
client_email is added as an OWNER of the Search Console property.
"""
import os
import logging

from config import settings

logger = logging.getLogger(__name__)

_SCOPES = ["https://www.googleapis.com/auth/indexing"]
_ENDPOINT = "https://indexing.googleapis.com/v3/urlNotifications:publish"
_session = None
_loaded = False


def _get_session():
    global _session, _loaded
    if _loaded:
        return _session
    _loaded = True
    keyfile = settings.GOOGLE_INDEXING_KEY_FILE
    if not keyfile or not os.path.exists(keyfile):
        logger.info("Indexing API: no key file configured — auto-indexing disabled.")
        return None
    try:
        from google.oauth2 import service_account
        from google.auth.transport.requests import AuthorizedSession
        creds = service_account.Credentials.from_service_account_file(keyfile, scopes=_SCOPES)
        _session = AuthorizedSession(creds)
        logger.info("Indexing API: authenticated.")
    except Exception as e:
        logger.error(f"Indexing API auth failed: {e}")
        _session = None
    return _session


def is_configured() -> bool:
    return _get_session() is not None


def submit_url(url: str, action: str = "URL_UPDATED") -> dict:
    """Notify Google to (re)crawl a URL. action = URL_UPDATED | URL_DELETED."""
    if not url:
        return {"ok": False, "detail": "no url"}
    session = _get_session()
    if session is None:
        return {"ok": False, "detail": "indexing not configured"}
    try:
        r = session.post(_ENDPOINT, json={"url": url, "type": action}, timeout=20)
        ok = r.status_code == 200
        if not ok:
            logger.warning(f"Indexing submit {url} -> {r.status_code}: {r.text[:200]}")
        return {"ok": ok, "status": r.status_code, "detail": r.text[:300]}
    except Exception as e:
        logger.error(f"Indexing submit error for {url}: {e}")
        return {"ok": False, "detail": str(e)}
