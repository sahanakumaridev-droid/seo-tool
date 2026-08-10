from fastapi import APIRouter
from pydantic import BaseModel
from models.schemas import (
    GoogleAdsCampaignRequest,
    GoogleAdsCampaignResult,
    GoogleAdsSuggestRequest,
    GoogleAdsLaunchRequest,
)
from services.google_ads_service import (
    create_campaign,
    is_configured,
    suggest_ad_copy,
    probe_connection,
    list_campaigns,
    set_campaign_status,
)
from providers.demo_google import use_demo_fallback
from services.llm_service import active_provider, llm_available
from config import settings

router = APIRouter()


class CampaignStatusRequest(BaseModel):
    campaign_id: str
    enable: bool = True


def _fmt_cid(raw: str) -> str:
    digits = (raw or "").replace("-", "")
    if len(digits) == 10:
        return f"{digits[:3]}-{digits[3:6]}-{digits[6:]}"
    return digits or ""


@router.get("/status")
async def get_status():
    creds = is_configured()
    api_ok, detail = probe_connection() if creds else (False, "Missing GOOGLE_ADS_* credentials")
    live = api_ok
    demo = use_demo_fallback(live)
    llm = active_provider() if llm_available() else None
    if live:
        mode = "live"
    elif llm:
        mode = "ai"
    elif demo:
        mode = "demo"
    else:
        mode = "setup"

    customer = _fmt_cid(settings.GOOGLE_ADS_CUSTOMER_ID)
    login = _fmt_cid(settings.GOOGLE_ADS_LOGIN_CUSTOMER_ID)
    return {
        "configured": live or demo,
        "credentials_present": creds,
        "demo": demo,
        "live": live,
        "detail": detail,
        "llm_provider": llm,
        "mode": mode,
        "customer_id": customer,
        "login_customer_id": login,
        "auto_create_on_publish": bool(settings.GOOGLE_ADS_AUTO_CREATE_ON_PUBLISH),
        "auto_enable": bool(settings.GOOGLE_ADS_AUTO_ENABLE),
        "open_hint": (
            f"In Google Ads account picker open manager {login or 'ZeOrbit Ads Manager'}, "
            f"then client {customer or '(set GOOGLE_ADS_CUSTOMER_ID)'}."
        ),
        "campaigns_url": (
            f"https://ads.google.com/aw/campaigns?__c={settings.GOOGLE_ADS_CUSTOMER_ID.replace('-', '')}"
            if settings.GOOGLE_ADS_CUSTOMER_ID else "https://ads.google.com/aw/campaigns"
        ),
    }


@router.get("/campaigns")
async def get_campaigns(limit: int = 50):
    """List campaigns so enable/pause can be done inside the SEO tool."""
    return list_campaigns(limit=limit)


@router.post("/campaigns/status")
async def update_campaign_status(req: CampaignStatusRequest):
    """Enable (go live) or pause a campaign without using the Google Ads UI."""
    return set_campaign_status(req.campaign_id, enable=req.enable)


@router.post("/suggest")
async def suggest_campaign_copy(req: GoogleAdsSuggestRequest):
    """Free AI (Groq/Gemini) or template ad copy — no Ads spend."""
    return await suggest_ad_copy(req)


@router.post("/create-campaign", response_model=GoogleAdsCampaignResult)
async def create_campaign_route(req: GoogleAdsCampaignRequest):
    return await create_campaign(req)


@router.post("/launch", response_model=GoogleAdsCampaignResult)
async def launch_from_landing(req: GoogleAdsLaunchRequest):
    """One-shot automation: generate copy + create Search campaign for a public URL."""
    copy = await suggest_ad_copy(
        GoogleAdsSuggestRequest(
            business_name=req.business_name,
            category=req.category,
            city=req.city,
        )
    )
    keywords = list(req.keywords or []) or list(copy.get("keywords") or [])
    name = f"{req.category or req.business_name or 'SEO'} - {req.city or 'Local'}".strip(" -")
    return await create_campaign(
        GoogleAdsCampaignRequest(
            campaign_name=name[:100] or "SEO Landing Campaign",
            daily_budget=req.daily_budget,
            final_url=req.final_url,
            headlines=(copy.get("headlines") or ["Local Pros Near You", "Book Today", "Free Quote"])[:15],
            descriptions=(copy.get("descriptions") or ["Trusted local service.", "Get a free quote today."])[:4],
            keywords=keywords[:8] or ["local services"],
            enable=req.enable or bool(settings.GOOGLE_ADS_AUTO_ENABLE),
        )
    )
