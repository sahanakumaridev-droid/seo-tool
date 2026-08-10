"""
google_ads_service.py
Creates a Search campaign (budget → campaign → ad group → keywords →
responsive search ad) via the official Google Ads API client library.
Credential-gated like the other social/GBP integrations: returns a clear
"not configured" / "not installed" result instead of raising when the
account isn't wired up yet.
"""
import re
import uuid
from typing import Optional
from urllib.parse import urlparse

from models.schemas import GoogleAdsCampaignRequest, GoogleAdsCampaignResult
from config import settings

_REQUIRED_SETTINGS = (
    "GOOGLE_ADS_DEVELOPER_TOKEN", "GOOGLE_ADS_CLIENT_ID", "GOOGLE_ADS_CLIENT_SECRET",
    "GOOGLE_ADS_REFRESH_TOKEN", "GOOGLE_ADS_CUSTOMER_ID",
)

# Google Ads rejects any final URL whose host has no real top-level domain
# (e.g. "localhost", "zeorbit", "192.168.1.1") with a confusing error that
# talks about the "tracking url template" even though it's the Final URL.
# Catch that here with a clear message instead of a failed API round trip.
_TLD_RE = re.compile(r"^[a-z0-9-]+(\.[a-z0-9-]+)*\.[a-z]{2,}$", re.IGNORECASE)


def normalize_final_url(raw: str) -> str:
    """Add a scheme if missing so urlparse can extract the host correctly."""
    raw = raw.strip()
    if raw and "://" not in raw:
        raw = f"https://{raw}"
    return raw


def _validate_final_url(raw: str) -> Optional[str]:
    """Return an error message if the URL isn't usable as a Google Ads Final
    URL, else None."""
    url = normalize_final_url(raw)
    parsed = urlparse(url)
    host = (parsed.hostname or "").strip()
    if not host or not _TLD_RE.match(host):
        return (
            f'"{raw}" isn\'t a valid public website URL. Enter a real domain '
            'with a top-level extension, like https://example.com — Google Ads '
            'can\'t target localhost, IP addresses, or bare names.'
        )
    return None


def is_configured() -> bool:
    return all(getattr(settings, key) for key in _REQUIRED_SETTINGS)


def probe_connection() -> tuple[bool, str]:
    """Hit Google Ads API for real. Returns (ok, detail). No mock."""
    if not is_configured():
        return False, "Missing GOOGLE_ADS_* credentials"
    try:
        from google.ads.googleads.errors import GoogleAdsException
    except ImportError:
        return False, "google-ads package not installed (pip install google-ads)"
    try:
        client = _build_client()
        customer_id = _customer_id()
        ga = client.get_service("GoogleAdsService")
        query = "SELECT customer.id FROM customer LIMIT 1"
        for batch in ga.search_stream(customer_id=customer_id, query=query):
            if batch.results:
                return True, f"customer {customer_id}"
        return True, f"customer {customer_id}"
    except Exception as e:
        msg = str(e)
        if "invalid_grant" in msg or "expired" in msg.lower() or "revoked" in msg.lower():
            return False, (
                "Refresh token expired/revoked. Run: "
                "python3 scripts/get_google_ads_refresh_token.py"
            )
        return False, msg[:300]


def _build_client():
    from google.ads.googleads.client import GoogleAdsClient  # optional dep

    config = {
        "developer_token": settings.GOOGLE_ADS_DEVELOPER_TOKEN,
        "client_id": settings.GOOGLE_ADS_CLIENT_ID,
        "client_secret": settings.GOOGLE_ADS_CLIENT_SECRET,
        "refresh_token": settings.GOOGLE_ADS_REFRESH_TOKEN,
        "use_proto_plus": True,
    }
    if settings.GOOGLE_ADS_LOGIN_CUSTOMER_ID:
        config["login_customer_id"] = settings.GOOGLE_ADS_LOGIN_CUSTOMER_ID
    return GoogleAdsClient.load_from_dict(config)


def _customer_id() -> str:
    return settings.GOOGLE_ADS_CUSTOMER_ID.replace("-", "")


def _create_budget(client, customer_id: str, name: str, daily_budget: float) -> str:
    service = client.get_service("CampaignBudgetService")
    operation = client.get_type("CampaignBudgetOperation")
    budget = operation.create
    budget.name = f"{name} Budget {uuid.uuid4().hex[:8]}"
    budget.amount_micros = int(round(daily_budget * 1_000_000))
    budget.delivery_method = client.enums.BudgetDeliveryMethodEnum.STANDARD
    response = service.mutate_campaign_budgets(customer_id=customer_id, operations=[operation])
    return response.results[0].resource_name


def _create_campaign(client, customer_id: str, name: str, budget_resource_name: str, *, enable: bool = False) -> str:
    service = client.get_service("CampaignService")
    operation = client.get_type("CampaignOperation")
    campaign = operation.create
    campaign.name = f"{name} {uuid.uuid4().hex[:8]}"
    campaign.advertising_channel_type = client.enums.AdvertisingChannelTypeEnum.SEARCH
    # Default PAUSED ($0). Only ENABLE when explicitly requested / env auto-enable.
    campaign.status = (
        client.enums.CampaignStatusEnum.ENABLED
        if enable
        else client.enums.CampaignStatusEnum.PAUSED
    )
    # Assigning the message (not just touching a sub-field) is required to
    # actually set the `campaign_bidding_strategy` oneof — enhanced_cpc_enabled
    # isn't settable in this API version/context, so plain Manual CPC.
    campaign.manual_cpc = client.get_type("ManualCpc")
    campaign.campaign_budget = budget_resource_name
    campaign.network_settings.target_google_search = True
    campaign.network_settings.target_search_network = True
    campaign.network_settings.target_content_network = False
    campaign.network_settings.target_partner_search_network = False
    # Required as of API v25 on every new campaign (EU political ads transparency).
    campaign.contains_eu_political_advertising = (
        client.enums.EuPoliticalAdvertisingStatusEnum.DOES_NOT_CONTAIN_EU_POLITICAL_ADVERTISING
    )
    response = service.mutate_campaigns(customer_id=customer_id, operations=[operation])
    return response.results[0].resource_name


def _create_ad_group(client, customer_id: str, name: str, campaign_resource_name: str) -> str:
    service = client.get_service("AdGroupService")
    operation = client.get_type("AdGroupOperation")
    ad_group = operation.create
    ad_group.name = f"{name} Ad Group"
    ad_group.campaign = campaign_resource_name
    ad_group.status = client.enums.AdGroupStatusEnum.ENABLED
    ad_group.type_ = client.enums.AdGroupTypeEnum.SEARCH_STANDARD
    response = service.mutate_ad_groups(customer_id=customer_id, operations=[operation])
    return response.results[0].resource_name


def _add_keywords(client, customer_id: str, ad_group_resource_name: str, keywords: list[str]) -> None:
    service = client.get_service("AdGroupCriterionService")
    operations = []
    for kw in keywords:
        operation = client.get_type("AdGroupCriterionOperation")
        criterion = operation.create
        criterion.ad_group = ad_group_resource_name
        criterion.status = client.enums.AdGroupCriterionStatusEnum.ENABLED
        criterion.keyword.text = kw
        criterion.keyword.match_type = client.enums.KeywordMatchTypeEnum.BROAD
        operations.append(operation)
    service.mutate_ad_group_criteria(customer_id=customer_id, operations=operations)


def _create_responsive_search_ad(client, customer_id: str, ad_group_resource_name: str,
                                  final_url: str, headlines: list[str], descriptions: list[str]) -> str:
    service = client.get_service("AdGroupAdService")
    operation = client.get_type("AdGroupAdOperation")
    ad_group_ad = operation.create
    ad_group_ad.ad_group = ad_group_resource_name
    ad_group_ad.status = client.enums.AdGroupAdStatusEnum.ENABLED
    ad_group_ad.ad.final_urls.append(final_url)
    for h in headlines[:15]:
        asset = client.get_type("AdTextAsset")
        asset.text = h[:30]
        ad_group_ad.ad.responsive_search_ad.headlines.append(asset)
    for d in descriptions[:4]:
        asset = client.get_type("AdTextAsset")
        asset.text = d[:90]
        ad_group_ad.ad.responsive_search_ad.descriptions.append(asset)
    response = service.mutate_ad_group_ads(customer_id=customer_id, operations=[operation])
    return response.results[0].resource_name


async def suggest_ad_copy(req) -> dict:
    """Free AI (Groq/Gemini) or local template — production-ready draft, $0 spend."""
    from services.llm_service import chat_json, active_provider

    name = (req.business_name or "Your Business").strip()
    cat = (req.category or "services").strip()
    city = (req.city or "").strip()
    prompt = (
        f"Generate Google Ads RSA copy for {name}, category {cat}"
        f"{f' in {city}' if city else ''}. "
        "Return JSON only with keys: headlines (array of 5 strings, each <=30 chars), "
        "descriptions (array of 2 strings, each <=90 chars), "
        "keywords (array of 4-6 search phrases). No emojis."
    )
    data = await chat_json(prompt, temperature=0.6, max_tokens=800)
    if data and isinstance(data.get("headlines"), list) and isinstance(data.get("descriptions"), list):
        return {
            "headlines": [str(h)[:30] for h in data["headlines"][:15]],
            "descriptions": [str(d)[:90] for d in data["descriptions"][:4]],
            "keywords": [str(k) for k in (data.get("keywords") or [])][:8],
            "source": "ai",
            "provider": active_provider(),
            "demo": False,
        }

    place = city
    cat_lower = cat.lower()
    headlines = [
        (f"{cat} in {place}" if place else cat)[:30],
        f"{cat} Experts"[:30],
        "Get a Free Quote"[:30],
        f"Call {name}"[:30],
        (f"Top-Rated Near {place}" if place else f"Top-Rated {cat}")[:30],
    ]
    descriptions = [
        f"{name} provides reliable {cat_lower}. Free quotes available."[:90],
        (f"Serving {place}. Fast, affordable, book online." if place else "Fast, affordable service. Book online in minutes.")[:90],
    ]
    keywords = [cat_lower, f"{cat_lower} near me", f"{cat_lower} in {place}" if place else f"best {cat_lower}", f"affordable {cat_lower}"]
    return {
        "headlines": headlines,
        "descriptions": descriptions,
        "keywords": keywords,
        "source": "template",
        "provider": None,
        "demo": False,
    }


async def create_campaign(req: GoogleAdsCampaignRequest) -> GoogleAdsCampaignResult:
    from providers.demo_google import use_demo_fallback, demo_ads_campaign

    # Live Google Ads API first (free to call; campaigns created PAUSED = $0 spend).
    if not is_configured():
        if use_demo_fallback(live_configured=False):
            data = demo_ads_campaign(req.campaign_name)
            return GoogleAdsCampaignResult(**data)
        return GoogleAdsCampaignResult(
            success=False,
            error=(
                "Google Ads isn't connected. Set GOOGLE_ADS_* credentials "
                "(API is free; use a test account or keep campaigns paused). "
                "Ad copy AI still works with GROQ_API_KEY or GEMINI_API_KEY."
            ),
        )

    url_error = _validate_final_url(req.final_url)
    if url_error:
        return GoogleAdsCampaignResult(success=False, error=url_error)
    final_url = normalize_final_url(req.final_url)

    try:
        from google.ads.googleads.errors import GoogleAdsException
    except ImportError:
        if use_demo_fallback(live_configured=False):
            return GoogleAdsCampaignResult(**demo_ads_campaign(req.campaign_name))
        return GoogleAdsCampaignResult(
            success=False,
            error="google-ads package not installed. Run: pip install google-ads",
        )

    try:
        client = _build_client()
        customer_id = _customer_id()

        budget_resource_name = _create_budget(client, customer_id, req.campaign_name, req.daily_budget)
        enable = bool(getattr(req, "enable", False) or settings.GOOGLE_ADS_AUTO_ENABLE)
        campaign_resource_name = _create_campaign(
            client, customer_id, req.campaign_name, budget_resource_name, enable=enable
        )
        ad_group_resource_name = _create_ad_group(client, customer_id, req.campaign_name, campaign_resource_name)
        _add_keywords(client, customer_id, ad_group_resource_name, req.keywords)
        _create_responsive_search_ad(
            client, customer_id, ad_group_resource_name, final_url, req.headlines, req.descriptions
        )

        campaign_id = campaign_resource_name.split("/")[-1]
        cid = customer_id
        return GoogleAdsCampaignResult(
            success=True,
            campaign_id=campaign_id,
            campaign_resource_name=campaign_resource_name,
            ad_group_resource_name=ad_group_resource_name,
            manage_url=(
                f"https://ads.google.com/aw/campaigns?campaignId={campaign_id}"
                f"&__c={cid}"
            ),
            demo=False,
        )
    except GoogleAdsException as ex:
        if use_demo_fallback(live_configured=False):
            return GoogleAdsCampaignResult(**demo_ads_campaign(req.campaign_name))
        details = "; ".join(err.message for err in ex.failure.errors)
        return GoogleAdsCampaignResult(success=False, error=f"Google Ads API error: {details}")
    except Exception as e:
        if use_demo_fallback(live_configured=False):
            return GoogleAdsCampaignResult(**demo_ads_campaign(req.campaign_name))
        return GoogleAdsCampaignResult(success=False, error=str(e))


def list_campaigns(limit: int = 50) -> dict:
    """Return recent campaigns in the configured customer account."""
    if not is_configured():
        return {"ok": False, "error": "Google Ads not configured", "campaigns": []}
    try:
        client = _build_client()
        customer_id = _customer_id()
        ga = client.get_service("GoogleAdsService")
        query = f"""
            SELECT campaign.id, campaign.name, campaign.status,
                   campaign_budget.amount_micros, campaign.bidding_strategy_type
            FROM campaign
            ORDER BY campaign.id DESC
            LIMIT {max(1, min(int(limit), 100))}
        """
        campaigns = []
        for batch in ga.search_stream(customer_id=customer_id, query=query):
            for row in batch.results:
                status = row.campaign.status.name if hasattr(row.campaign.status, "name") else str(row.campaign.status)
                budget = (row.campaign_budget.amount_micros or 0) / 1_000_000
                campaigns.append({
                    "id": str(row.campaign.id),
                    "name": row.campaign.name,
                    "status": status,
                    "daily_budget": budget,
                    "manage_url": (
                        f"https://ads.google.com/aw/campaigns?campaignId={row.campaign.id}"
                        f"&__c={customer_id}"
                    ),
                })
        return {"ok": True, "customer_id": customer_id, "campaigns": campaigns}
    except Exception as e:
        return {"ok": False, "error": str(e)[:500], "campaigns": []}


def set_campaign_status(campaign_id: str, enable: bool = True) -> dict:
    """Enable or pause a campaign from the SEO tool (no Google Ads UI needed)."""
    if not is_configured():
        return {"ok": False, "error": "Google Ads not configured"}
    cid = str(campaign_id or "").strip()
    if not cid.isdigit():
        return {"ok": False, "error": "Invalid campaign_id"}
    try:
        from google.protobuf import field_mask_pb2

        client = _build_client()
        customer_id = _customer_id()
        service = client.get_service("CampaignService")
        operation = client.get_type("CampaignOperation")
        campaign = operation.update
        campaign.resource_name = service.campaign_path(customer_id, cid)
        campaign.status = (
            client.enums.CampaignStatusEnum.ENABLED
            if enable
            else client.enums.CampaignStatusEnum.PAUSED
        )
        operation.update_mask.CopyFrom(field_mask_pb2.FieldMask(paths=["status"]))
        service.mutate_campaigns(customer_id=customer_id, operations=[operation])
        return {
            "ok": True,
            "campaign_id": cid,
            "status": "ENABLED" if enable else "PAUSED",
            "note": (
                "Campaign enabled in your tool. Google may still show 'Under review' "
                "until their automatic policy check finishes — that cannot be skipped by any tool."
                if enable else "Campaign paused."
            ),
        }
    except Exception as e:
        return {"ok": False, "error": str(e)[:500]}
