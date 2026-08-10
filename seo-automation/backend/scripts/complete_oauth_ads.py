"""
Secure Google Ads OAuth capture — writes refresh token to .env only.
Never prints the token value.
"""
from __future__ import annotations

import os
import re
import sys
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import settings  # noqa: E402

HOST = "127.0.0.1"
PORT = 8080
REDIRECT_URI = f"http://{HOST}:{PORT}/"
SCOPES = ["https://www.googleapis.com/auth/adwords"]
ENV_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")


def _upsert_env(key: str, value: str) -> None:
    text = ""
    if os.path.exists(ENV_PATH):
        with open(ENV_PATH, "r", encoding="utf-8") as f:
            text = f.read()
    pattern = re.compile(rf"^{re.escape(key)}=.*$", re.MULTILINE)
    line = f"{key}={value}"
    if pattern.search(text):
        text = pattern.sub(line, text)
    else:
        if text and not text.endswith("\n"):
            text += "\n"
        text += line + "\n"
    with open(ENV_PATH, "w", encoding="utf-8") as f:
        f.write(text)


def _verify_refresh(refresh_token: str) -> tuple[bool, str]:
    import httpx
    r = httpx.post(
        "https://oauth2.googleapis.com/token",
        data={
            "client_id": settings.GOOGLE_ADS_CLIENT_ID,
            "client_secret": settings.GOOGLE_ADS_CLIENT_SECRET,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        },
        timeout=30,
    )
    if r.status_code != 200:
        return False, f"token exchange HTTP {r.status_code}"
    data = r.json()
    if not data.get("access_token"):
        return False, "no access_token in response"
    return True, "access_token_ok"


def main() -> int:
    if not settings.GOOGLE_ADS_CLIENT_ID or not settings.GOOGLE_ADS_CLIENT_SECRET:
        print("FAIL: GOOGLE_ADS_CLIENT_ID/SECRET missing in .env")
        return 1

    from google_auth_oauthlib.flow import Flow

    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": settings.GOOGLE_ADS_CLIENT_ID,
                "client_secret": settings.GOOGLE_ADS_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [REDIRECT_URI, f"http://localhost:{PORT}/"],
            }
        },
        scopes=SCOPES,
    )
    flow.redirect_uri = REDIRECT_URI
    auth_url, _ = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",
    )

    result = {"code": None, "error": None}

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            qs = parse_qs(urlparse(self.path).query)
            if "code" in qs:
                result["code"] = qs["code"][0]
                body = b"<h1>Authorized</h1><p>Return to Cursor. You can close this tab.</p>"
                self.send_response(200)
            else:
                result["error"] = qs.get("error", ["unknown"])[0]
                body = b"<h1>Failed</h1><p>Return to Cursor.</p>"
                self.send_response(400)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *args):
            return

    server = HTTPServer((HOST, PORT), Handler)

    def serve():
        while result["code"] is None and result["error"] is None:
            server.handle_request()

    t = threading.Thread(target=serve, daemon=True)
    t.start()

    print("STATUS: waiting_for_google_login")
    print(f"REDIRECT_URI: {REDIRECT_URI}")
    print("ACTION_REQUIRED: In the browser that opens, sign in and click Allow.")
    webbrowser.open(auth_url)

    t.join(timeout=300)
    server.server_close()

    if result["error"]:
        print(f"FAIL: oauth_error={result['error']}")
        return 1
    if not result["code"]:
        print("FAIL: timeout_waiting_for_authorization")
        return 1

    flow.fetch_token(code=result["code"])
    refresh = flow.credentials.refresh_token
    if not refresh:
        print("FAIL: no_refresh_token (revoke app access at myaccount.google.com/permissions and retry)")
        return 1

    _upsert_env("GOOGLE_ADS_REFRESH_TOKEN", refresh)
    _upsert_env("DEMO_MODE", "false")

    ok, detail = _verify_refresh(refresh)
    if not ok:
        print(f"FAIL: refresh_verify={detail}")
        return 1

    print("SUCCESS: refresh_token_saved_to_env")
    print("SUCCESS: access_token_verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
