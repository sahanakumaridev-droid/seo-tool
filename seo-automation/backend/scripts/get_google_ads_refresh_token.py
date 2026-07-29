"""
One-time helper to generate a Google Ads API refresh token.

Reads GOOGLE_ADS_CLIENT_ID / GOOGLE_ADS_CLIENT_SECRET from backend/.env,
opens your browser for you to sign in and grant access, then prints the
refresh token to paste into GOOGLE_ADS_REFRESH_TOKEN in that same .env file.

Run from the backend/ directory with the venv active:
    python scripts/get_google_ads_refresh_token.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import settings  # noqa: E402

SCOPES = ["https://www.googleapis.com/auth/adwords"]


def main():
    if not settings.GOOGLE_ADS_CLIENT_ID or not settings.GOOGLE_ADS_CLIENT_SECRET:
        print("Missing GOOGLE_ADS_CLIENT_ID or GOOGLE_ADS_CLIENT_SECRET in backend/.env — set those first.")
        sys.exit(1)

    from google_auth_oauthlib.flow import InstalledAppFlow

    client_config = {
        "installed": {
            "client_id": settings.GOOGLE_ADS_CLIENT_ID,
            "client_secret": settings.GOOGLE_ADS_CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": ["http://localhost"],
        }
    }

    flow = InstalledAppFlow.from_client_config(client_config, scopes=SCOPES)
    print("Opening your browser — sign in with the Google account that has access to your Google Ads account,")
    print("and approve the request. Come back here once you've approved it.\n")
    credentials = flow.run_local_server(port=0)

    print("\n" + "=" * 60)
    print("Your refresh token (paste this as GOOGLE_ADS_REFRESH_TOKEN in .env):\n")
    print(credentials.refresh_token)
    print("=" * 60)


if __name__ == "__main__":
    main()
