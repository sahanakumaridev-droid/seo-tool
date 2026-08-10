"""
One-time helper: get a Google Business Profile refresh token (LIVE posts).

Uses the same OAuth client as Google Ads (GOOGLE_ADS_CLIENT_ID / SECRET).
Requires the Business Profile APIs enabled in that Cloud project.

Run from backend/:
    python3 scripts/get_gbp_refresh_token.py

Then paste into .env:
    GBP_REFRESH_TOKEN=...
    GBP_ACCOUNT_ID=...      # from the printed account list
    GBP_LOCATION_ID=...     # from the printed location list
"""
import os
import sys

import httpx

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import settings  # noqa: E402

# business.manage covers GBP local posts / locations
SCOPES = ["https://www.googleapis.com/auth/business.manage"]
REDIRECT_PORT = 8080
REDIRECT_URIS = [
    f"http://127.0.0.1:{REDIRECT_PORT}/",
    f"http://localhost:{REDIRECT_PORT}/",
]


def main():
    if not settings.GOOGLE_ADS_CLIENT_ID or not settings.GOOGLE_ADS_CLIENT_SECRET:
        print("Set GOOGLE_ADS_CLIENT_ID and GOOGLE_ADS_CLIENT_SECRET in backend/.env first.")
        sys.exit(1)

    from google_auth_oauthlib.flow import InstalledAppFlow

    client_config = {
        "installed": {
            "client_id": settings.GOOGLE_ADS_CLIENT_ID,
            "client_secret": settings.GOOGLE_ADS_CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": REDIRECT_URIS,
        }
    }

    flow = InstalledAppFlow.from_client_config(client_config, scopes=SCOPES)
    print("Confirm Cloud Console Authorized redirect URIs include:")
    for u in REDIRECT_URIS:
        print(f"  • {u}")
    print()
    print("Opening browser — sign in with the Google account that manages your Business Profile.")
    print("Approve Business Profile access, then return here.\n")
    credentials = flow.run_local_server(
        host="127.0.0.1",
        port=REDIRECT_PORT,
        redirect_uri_trailing_slash=True,
    )

    print("\n" + "=" * 60)
    print("Paste into backend/.env:\n")
    print(f"GBP_REFRESH_TOKEN={credentials.refresh_token}")
    print("=" * 60)

    token = credentials.token
    headers = {"Authorization": f"Bearer {token}"}

    # List accounts (Account Management API)
    print("\nFetching GBP accounts…")
    try:
        r = httpx.get(
            "https://mybusinessaccountmanagement.googleapis.com/v1/accounts",
            headers=headers,
            timeout=30,
        )
        print(f"accounts HTTP {r.status_code}")
        data = r.json() if r.status_code == 200 else {}
        accounts = data.get("accounts") or []
        if not accounts:
            print("No accounts returned. Enable 'My Business Account Management API' in Cloud Console")
            print("and ensure this Google user owns a Business Profile.")
            print(r.text[:400])
            return

        for acc in accounts:
            name = acc.get("name", "")  # accounts/123
            account_id = name.split("/")[-1] if name else ""
            print(f"\nAccount: {acc.get('accountName') or acc.get('type')}  →  GBP_ACCOUNT_ID={account_id}")

            # List locations
            lr = httpx.get(
                f"https://mybusinessbusinessinformation.googleapis.com/v1/{name}/locations",
                headers=headers,
                params={"readMask": "name,title,storefrontAddress"},
                timeout=30,
            )
            if lr.status_code != 200:
                print(f"  locations HTTP {lr.status_code}: {lr.text[:200]}")
                print("  Enable 'My Business Business Information API' in Cloud Console.")
                continue
            locs = (lr.json() or {}).get("locations") or []
            if not locs:
                print("  (no locations)")
            for loc in locs:
                lname = loc.get("name", "")  # accounts/x/locations/y OR locations/y
                location_id = lname.split("/")[-1]
                title = loc.get("title") or ""
                print(f"  Location: {title}  →  GBP_LOCATION_ID={location_id}")
    except Exception as e:
        print(f"Lookup failed: {e}")
        print("You can still set GBP_ACCOUNT_ID / GBP_LOCATION_ID from Google Business Profile Manager.")


if __name__ == "__main__":
    main()
