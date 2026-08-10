"""
Live Google automation status — no mock. Used by dashboard to show what's
actually connected for Ads / Indexing (GSC) / Business Profile.
"""
from fastapi import APIRouter

from config import settings
from providers.demo_google import demo_enabled
from services.google_ads_service import is_configured as ads_configured, probe_connection
from services.social_service import gbp_configured
from services import search_console_service
from services.llm_service import active_provider, llm_available
import os

router = APIRouter()


@router.get("/live-status")
async def google_live_status():
    ads_creds = ads_configured()
    ads_ok, ads_detail = probe_connection() if ads_creds else (False, "Missing GOOGLE_ADS_* credentials")
    gsc_live = search_console_service.is_configured()
    gbp_live = gbp_configured()
    key = settings.GOOGLE_INDEXING_KEY_FILE or ""

    ads_blocking = []
    if not ads_ok:
        if not ads_creds:
            ads_blocking = [
                "Set GOOGLE_ADS_DEVELOPER_TOKEN, CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN, CUSTOMER_ID",
            ]
        else:
            ads_blocking = [ads_detail]

    return {
        "demo_mode": demo_enabled(),
        "mock_data_possible": demo_enabled(),
        "modules": {
            "google_ads": {
                "live": ads_ok,
                "ready": ads_ok and not demo_enabled(),
                "credentials_present": ads_creds,
                "detail": ads_detail,
                "blocking": ads_blocking,
                "docs": "https://developers.google.com/google-ads/api/docs/get-started",
                "fix_cmd": "python3 scripts/get_google_ads_refresh_token.py",
            },
            "google_indexing": {
                "live": gsc_live,
                "ready": gsc_live and not demo_enabled(),
                "crawl_fallback": not gsc_live,
                "blocking": (
                    [] if gsc_live else [
                        "Enable Search Console API in Google Cloud",
                        "Create service account JSON + add as Owner in Search Console",
                        "Set GSC_SITE_URL and GOOGLE_INDEXING_KEY_FILE",
                        "Set WP_SITEMAP_URL for sitemap automation",
                    ]
                ),
                "key_file_exists": bool(key) and os.path.exists(key),
                "gsc_site_url": bool(settings.GSC_SITE_URL),
                "docs": "https://developers.google.com/webmaster-tools/v1/how-tos/search-console-api",
            },
            "google_business_profile": {
                "live": gbp_live,
                "ready": gbp_live and not demo_enabled(),
                "blocking": (
                    [] if gbp_live else [
                        "Enable My Business Account Management + Business Information + My Business APIs",
                        "Run: python3 scripts/get_gbp_refresh_token.py",
                        "Set GBP_REFRESH_TOKEN, GBP_ACCOUNT_ID, GBP_LOCATION_ID",
                    ]
                ),
                "docs": "https://developers.google.com/my-business/content/basic-setup",
                "fix_cmd": "python3 scripts/get_gbp_refresh_token.py",
            },
        },
        "free_ai": {
            "ready": llm_available(),
            "provider": active_provider(),
            "blocking": [] if llm_available() else [
                "Add GROQ_API_KEY (https://console.groq.com/keys) or GEMINI_API_KEY (https://aistudio.google.com/app/apikey)",
            ],
        },
        "all_google_live": ads_ok and gsc_live and gbp_live and not demo_enabled(),
    }
