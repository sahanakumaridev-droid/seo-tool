"""
verify_google_live.py — check which Google automations are LIVE (no mock).

Run from backend/:
    python3 scripts/verify_google_live.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import settings  # noqa: E402
from providers.demo_google import demo_enabled  # noqa: E402
from services.google_ads_service import is_configured as ads_configured  # noqa: E402
from services.social_service import gbp_configured  # noqa: E402
from services import search_console_service  # noqa: E402


def section(title: str):
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


def main():
    section("GLOBAL")
    print(f"DEMO_MODE = {settings.DEMO_MODE}  (must be False for live automation)")
    if demo_enabled():
        print("BLOCKED: turn off DEMO_MODE in .env")

    section("1) GOOGLE ADS (create paused campaigns)")
    if not ads_configured():
        print("NOT LIVE — missing GOOGLE_ADS_* credentials")
        print("Get: Ads API Center developer token + OAuth client")
        print("Refresh token: python3 scripts/get_google_ads_refresh_token.py")
    else:
        print("Credentials present — testing API…")
        try:
            from services.google_ads_service import _build_client, _customer_id
            client = _build_client()
            cid = _customer_id()
            ga = client.get_service("GoogleAdsService")
            q = "SELECT customer.id, customer.descriptive_name FROM customer LIMIT 1"
            ok = False
            for batch in ga.search_stream(customer_id=cid, query=q):
                for row in batch.results:
                    print(f"LIVE OK — customer {row.customer.id} ({row.customer.descriptive_name})")
                    ok = True
                    break
            if not ok:
                print("LIVE FAIL — empty customer response")
        except Exception as e:
            print(f"NOT LIVE — API error: {e}")
            print("Fix: re-run python3 scripts/get_google_ads_refresh_token.py (token expired/revoked)")

    section("2) GOOGLE INDEXING (Search Console — real index status)")
    key = settings.GOOGLE_INDEXING_KEY_FILE
    print(f"GSC_SITE_URL = {settings.GSC_SITE_URL or '(empty)'}")
    print(f"WP_SITEMAP_URL = {settings.WP_SITEMAP_URL or '(empty)'}")
    print(f"GOOGLE_INDEXING_KEY_FILE = {key or '(empty)'}")
    if key and not os.path.exists(key):
        print(f"KEY FILE MISSING on disk: {key}")
    if search_console_service.is_configured():
        print("LIVE OK — Search Console client ready")
        print("Automation: refresh /seo-indexing uses URL Inspection API")
    else:
        print("NOT LIVE — do this:")
        print("  1. https://console.cloud.google.com → enable Search Console API")
        print("  2. Create Service Account → download JSON key")
        print("  3. https://search.google.com/search-console → Users → add SA email as Owner")
        print("  4. .env: GSC_SITE_URL=https://yoursite.com/")
        print("  5. .env: GOOGLE_INDEXING_KEY_FILE=/absolute/path/to/key.json")
        print("  6. .env: WP_SITEMAP_URL=https://yoursite.com/sitemap_index.xml")

    section("3) GOOGLE BUSINESS PROFILE (live local posts)")
    if gbp_configured():
        print("Credentials present — LIVE publish path enabled")
        print("(Post from /gbp UI to verify against Google)")
    else:
        print("NOT LIVE — do this:")
        print("  1. Cloud Console → enable:")
        print("     - My Business Account Management API")
        print("     - My Business Business Information API")
        print("     - Google My Business API (for localPosts)")
        print("  2. python3 scripts/get_gbp_refresh_token.py")
        print("  3. Paste GBP_REFRESH_TOKEN, GBP_ACCOUNT_ID, GBP_LOCATION_ID into .env")
        print("  4. Restart backend")

    section("SUMMARY")
    print("Live automation needs ALL THREE configured + DEMO_MODE=false.")
    print("No mock data is returned when DEMO_MODE=false.")


if __name__ == "__main__":
    main()
