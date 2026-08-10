"""
Generate a Google Ads API refresh token (robust OAuth helper).

Fixes common issues:
  - redirect_uri_mismatch  → fixed port 8080 + exact URIs
  - invalid_request / missing response_type → opens browser itself;
    also writes the FULL URL to oauth_ads_url.txt (don't copy from a
    wrapped terminal line)

Google Cloud Console → your OAuth client → Authorized redirect URIs must include:
    http://127.0.0.1:8080/
    http://localhost:8080/

Preferred: use an OAuth client type "Desktop app" (easiest).
Web application clients also work if the redirect URIs above are saved.

Run:
    cd backend
    python3 scripts/get_google_ads_refresh_token.py
"""
from __future__ import annotations

import os
import sys
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import settings  # noqa: E402

SCOPES = ["https://www.googleapis.com/auth/adwords"]
HOST = "127.0.0.1"
PORT = 8080
REDIRECT_URI = f"http://{HOST}:{PORT}/"
URL_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "oauth_ads_url.txt")


def main():
    if not settings.GOOGLE_ADS_CLIENT_ID or not settings.GOOGLE_ADS_CLIENT_SECRET:
        print("Missing GOOGLE_ADS_CLIENT_ID / GOOGLE_ADS_CLIENT_SECRET in .env")
        sys.exit(1)

    from google_auth_oauthlib.flow import Flow

    client_config = {
        "web": {
            "client_id": settings.GOOGLE_ADS_CLIENT_ID,
            "client_secret": settings.GOOGLE_ADS_CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [
                REDIRECT_URI,
                f"http://localhost:{PORT}/",
            ],
        }
    }

    flow = Flow.from_client_config(client_config, scopes=SCOPES)
    flow.redirect_uri = REDIRECT_URI

    auth_url, _state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",  # force refresh_token
    )

    # Persist FULL URL so terminal line-wrapping can't break copy/paste
    with open(URL_FILE, "w", encoding="utf-8") as f:
        f.write(auth_url.strip() + "\n")

    print("=" * 60)
    print("STEP A — Cloud Console must allow this redirect URI:")
    print(f"  {REDIRECT_URI}")
    print(f"  http://localhost:{PORT}/")
    print()
    print("STEP B — Authorize (pick ONE):")
    print(f"  1) Open the file (easiest):  open {URL_FILE}")
    print("  2) Or wait — browser should open automatically")
    print()
    print("Sign in as the Google Ads owner → click Allow.")
    print("Do NOT open a truncated URL from the terminal.")
    print("=" * 60)

    # Catch the redirect with a tiny local server
    result = {"code": None, "error": None}

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            qs = parse_qs(urlparse(self.path).query)
            if "code" in qs:
                result["code"] = qs["code"][0]
                body = b"<h1>Success</h1><p>You can close this tab and return to Terminal.</p>"
                self.send_response(200)
            else:
                result["error"] = qs.get("error", ["unknown"])[0]
                body = b"<h1>Failed</h1><p>Return to Terminal.</p>"
                self.send_response(400)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, fmt, *args):
            return

    server = HTTPServer((HOST, PORT), Handler)

    def serve():
        while result["code"] is None and result["error"] is None:
            server.handle_request()

    t = threading.Thread(target=serve, daemon=True)
    t.start()

    try:
        webbrowser.open(auth_url)
    except Exception:
        pass

    print("\nWaiting for Google to redirect back to localhost:8080 …")
    t.join(timeout=300)
    server.server_close()

    if result["error"]:
        print(f"\nAuthorization failed: {result['error']}")
        sys.exit(1)
    if not result["code"]:
        print("\nTimed out waiting for approval. Re-run and use: open " + URL_FILE)
        sys.exit(1)

    flow.fetch_token(code=result["code"])
    creds = flow.credentials

    if not creds.refresh_token:
        print("\nNo refresh_token returned. Revoke prior access at")
        print("https://myaccount.google.com/permissions then run again.")
        sys.exit(1)

    print("\n" + "=" * 60)
    print("SUCCESS — paste this token in chat (or into .env as GOOGLE_ADS_REFRESH_TOKEN):\n")
    print(creds.refresh_token)
    print("=" * 60)


if __name__ == "__main__":
    main()
