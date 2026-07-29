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


def _create_campaign(client, customer_id: str, name: str, budget_resource_name: str) -> str:
    service = client.get_service("CampaignService")
    operation = client.get_type("CampaignOperation")
    campaign = operation.create
    campaign.name = f"{name} {uuid.uuid4().hex[:8]}"
    campaign.advertising_channel_type = client.enums.AdvertisingChannelTypeEnum.SEARCH
    # Created paused so nothing spends until a human reviews it in Google Ads.
    campaign.status = client.enums.CampaignStatusEnum.PAUSED
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


async def create_campaign(req: GoogleAdsCampaignRequest) -> GoogleAdsCampaignResult:
    if not is_configured():
        return GoogleAdsCampaignResult(success=False, error="Google Ads credentials not configured")

    url_error = _validate_final_url(req.final_url)
    if url_error:
        return GoogleAdsCampaignResult(success=False, error=url_error)
    final_url = normalize_final_url(req.final_url)

    try:
        from google.ads.googleads.errors import GoogleAdsException
    except ImportError:
        return GoogleAdsCampaignResult(
            success=False,
            error="google-ads package not installed. Run: pip install google-ads",
        )

    try:
        client = _build_client()
        customer_id = _customer_id()

        budget_resource_name = _create_budget(client, customer_id, req.campaign_name, req.daily_budget)
        campaign_resource_name = _create_campaign(client, customer_id, req.campaign_name, budget_resource_name)
        ad_group_resource_name = _create_ad_group(client, customer_id, req.campaign_name, campaign_resource_name)
        _add_keywords(client, customer_id, ad_group_resource_name, req.keywords)
        _create_responsive_search_ad(
            client, customer_id, ad_group_resource_name, final_url, req.headlines, req.descriptions
        )

        campaign_id = campaign_resource_name.split("/")[-1]
        return GoogleAdsCampaignResult(
            success=True,
            campaign_id=campaign_id,
            campaign_resource_name=campaign_resource_name,
            ad_group_resource_name=ad_group_resource_name,
            manage_url=f"https://ads.google.com/aw/campaigns?campaignId={campaign_id}",
        )
    except GoogleAdsException as ex:
        details = "; ".join(err.message for err in ex.failure.errors)
        return GoogleAdsCampaignResult(success=False, error=f"Google Ads API error: {details}")
    except Exception as e:
        return GoogleAdsCampaignResult(success=False, error=str(e))
