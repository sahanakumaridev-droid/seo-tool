"""
social_service.py
Automates social media posting to Facebook, Twitter/X, LinkedIn, Instagram.
"""
import httpx
from typing import List, Optional
from models.schemas import SocialPostRequest, SocialPostResult
from config import settings


# Per-platform character limits (hard caps we truncate to).
PLATFORM_LIMITS = {
    "twitter": 280,
    "x": 280,
    "threads": 500,
    "pinterest": 500,     # pin description
    "gbp": 1500,          # Google Business Profile post
    "facebook": 63206,
    "linkedin": 3000,
    "instagram": 2200,
}


def _hashtags(req: SocialPostRequest, n: int = 8) -> str:
    tags = [f"#{kw.replace(' ', '')}" for kw in req.keywords[:5] if kw]
    tags += [f"#{req.business_type.replace(' ', '')}", f"#{req.city.replace(' ', '')}", "#LocalSEO", "#SmallBusiness"]
    # de-dupe preserving order
    seen, out = set(), []
    for t in tags:
        if t.lower() not in seen:
            seen.add(t.lower()); out.append(t)
    return " ".join(out[:n])


def _build_caption(req: SocialPostRequest, platform: str) -> str:
    """Build a UNIQUE, platform-optimized caption (not duplicated across platforms)."""
    platform = platform.lower()
    hashtag_str = _hashtags(req)
    limit = PLATFORM_LIMITS.get(platform, 2200)

    if platform in ("twitter", "x"):
        # Punchy, hashtag-light, link-forward.
        base = f"{req.title}\n\n{req.post_url}"
        tags = f"\n\n{_hashtags(req, 3)}"
        text = base + tags
        return text if len(text) <= limit else (req.title[:limit - len(req.post_url) - 5] + f"\n{req.post_url}")

    elif platform == "linkedin":
        # Professional, insight-led, first-person value framing.
        text = (
            f"🚀 {req.title}\n\n"
            f"{req.meta_description}\n\n"
            f"📍 Serving {req.city} and the surrounding area.\n\n"
            f"Full article 👉 {req.post_url}\n\n"
            f"{hashtag_str}"
        )
        return text[:limit]

    elif platform == "facebook":
        # Conversational, question hook to drive engagement.
        text = (
            f"{req.title}\n\n"
            f"{req.meta_description}\n\n"
            f"👉 Read the full guide: {req.post_url}\n\n"
            f"{_hashtags(req, 5)}"
        )
        return text[:limit]

    elif platform == "instagram":
        # Emoji-rich, hashtag-heavy (IG rewards more tags).
        text = (
            f"✨ {req.title} ✨\n\n"
            f"{req.meta_description}\n\n"
            f"🔗 Link in bio / {req.post_url}\n\n"
            f"{_hashtags(req, 10)}"
        )
        return text[:limit]

    elif platform == "pinterest":
        # Keyword-rich description optimized for Pinterest search.
        text = (
            f"{req.title} — {req.meta_description} "
            f"Learn more about {req.business_type.lower()} in {req.city}: {req.post_url} "
            f"{_hashtags(req, 6)}"
        )
        return text[:limit]

    elif platform == "threads":
        # Casual, short, one strong hook + link.
        text = f"{req.title}\n\n{req.meta_description[:180]}\n\n{req.post_url}\n{_hashtags(req, 3)}"
        return text[:limit]

    elif platform == "gbp":
        # Google Business Profile: local, action-oriented, no hashtags (GBP ignores them).
        text = (
            f"{req.title}\n\n"
            f"{req.meta_description}\n\n"
            f"Serving {req.city} — read more: {req.post_url}"
        )
        return text[:limit]

    return f"{req.title}\n{req.post_url}"[:limit]


async def post_to_facebook(req: SocialPostRequest) -> SocialPostResult:
    """Post to a Facebook Page."""
    token = settings.FACEBOOK_ACCESS_TOKEN
    page_id = settings.FACEBOOK_PAGE_ID
    if not token or not page_id:
        return SocialPostResult(platform="facebook", success=False, error="Facebook credentials not configured")

    caption = _build_caption(req, "facebook")
    payload: dict = {"message": caption, "access_token": token}
    if req.image_url:
        payload["link"] = req.post_url

    try:
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.post(
                f"https://graph.facebook.com/v19.0/{page_id}/feed",
                data=payload,
            )
            data = resp.json()
            if "id" in data:
                post_id = data["id"]
                return SocialPostResult(
                    platform="facebook",
                    success=True,
                    post_id=post_id,
                    post_url=f"https://facebook.com/{post_id}",
                )
            return SocialPostResult(platform="facebook", success=False, error=str(data.get("error", data)))
    except Exception as e:
        return SocialPostResult(platform="facebook", success=False, error=str(e))


async def post_to_twitter(req: SocialPostRequest) -> SocialPostResult:
    """Post to Twitter/X using OAuth 1.0a."""
    api_key = settings.TWITTER_API_KEY
    api_secret = settings.TWITTER_API_SECRET
    access_token = settings.TWITTER_ACCESS_TOKEN
    access_secret = settings.TWITTER_ACCESS_SECRET

    if not all([api_key, api_secret, access_token, access_secret]):
        return SocialPostResult(platform="twitter", success=False, error="Twitter credentials not configured")

    try:
        import tweepy
        client = tweepy.AsyncClient(
            consumer_key=api_key,
            consumer_secret=api_secret,
            access_token=access_token,
            access_token_secret=access_secret,
        )
        text = _build_caption(req, "twitter")
        response = await client.create_tweet(text=text)
        tweet_id = response.data["id"]
        return SocialPostResult(
            platform="twitter",
            success=True,
            post_id=str(tweet_id),
            post_url=f"https://twitter.com/i/web/status/{tweet_id}",
        )
    except ImportError:
        return SocialPostResult(platform="twitter", success=False, error="tweepy not installed. Run: pip install tweepy")
    except Exception as e:
        return SocialPostResult(platform="twitter", success=False, error=str(e))


async def post_to_linkedin(req: SocialPostRequest) -> SocialPostResult:
    """Post to LinkedIn as a person or organization."""
    token = settings.LINKEDIN_ACCESS_TOKEN
    person_urn = settings.LINKEDIN_PERSON_URN
    if not token or not person_urn:
        return SocialPostResult(platform="linkedin", success=False, error="LinkedIn credentials not configured")

    caption = _build_caption(req, "linkedin")
    payload = {
        "author": person_urn,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": caption},
                "shareMediaCategory": "ARTICLE" if req.post_url else "NONE",
                "media": [
                    {
                        "status": "READY",
                        "originalUrl": req.post_url,
                        "title": {"text": req.title},
                        "description": {"text": req.meta_description[:200]},
                    }
                ] if req.post_url else [],
            }
        },
        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
    }

    try:
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.post(
                "https://api.linkedin.com/v2/ugcPosts",
                json=payload,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                    "X-Restli-Protocol-Version": "2.0.0",
                },
            )
            if resp.status_code in (200, 201):
                post_id = resp.json().get("id", "")
                return SocialPostResult(
                    platform="linkedin",
                    success=True,
                    post_id=post_id,
                    post_url=f"https://www.linkedin.com/feed/update/{post_id}",
                )
            return SocialPostResult(platform="linkedin", success=False, error=f"LinkedIn API {resp.status_code}: {resp.text[:200]}")
    except Exception as e:
        return SocialPostResult(platform="linkedin", success=False, error=str(e))


async def post_to_instagram(req: SocialPostRequest) -> SocialPostResult:
    """Post to Instagram Business account via Graph API (requires image)."""
    token = settings.INSTAGRAM_ACCESS_TOKEN
    account_id = settings.INSTAGRAM_ACCOUNT_ID
    if not token or not account_id:
        return SocialPostResult(platform="instagram", success=False, error="Instagram credentials not configured")
    if not req.image_url:
        return SocialPostResult(platform="instagram", success=False, error="Instagram requires an image URL")

    caption = _build_caption(req, "instagram")
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            # Step 1: Create media container
            container_resp = await client.post(
                f"https://graph.facebook.com/v19.0/{account_id}/media",
                data={
                    "image_url": req.image_url,
                    "caption": caption,
                    "access_token": token,
                },
            )
            container_data = container_resp.json()
            if "id" not in container_data:
                return SocialPostResult(platform="instagram", success=False, error=str(container_data.get("error", container_data)))

            container_id = container_data["id"]

            # Step 2: Publish the container
            publish_resp = await client.post(
                f"https://graph.facebook.com/v19.0/{account_id}/media_publish",
                data={"creation_id": container_id, "access_token": token},
            )
            publish_data = publish_resp.json()
            if "id" in publish_data:
                return SocialPostResult(platform="instagram", success=True, post_id=publish_data["id"])
            return SocialPostResult(platform="instagram", success=False, error=str(publish_data.get("error", publish_data)))
    except Exception as e:
        return SocialPostResult(platform="instagram", success=False, error=str(e))


async def post_to_pinterest(req: SocialPostRequest) -> SocialPostResult:
    """Create a Pin via the Pinterest API v5 (credential-gated)."""
    token = settings.PINTEREST_ACCESS_TOKEN
    board_id = settings.PINTEREST_BOARD_ID
    if not token or not board_id:
        return SocialPostResult(platform="pinterest", success=False, error="Pinterest credentials not configured")
    if not req.image_url:
        return SocialPostResult(platform="pinterest", success=False, error="Pinterest requires an image URL")

    payload = {
        "board_id": board_id,
        "title": req.title[:100],
        "description": _build_caption(req, "pinterest"),
        "link": req.post_url,
        "media_source": {"source_type": "image_url", "url": req.image_url},
    }
    try:
        async with httpx.AsyncClient(timeout=25) as client:
            resp = await client.post(
                "https://api.pinterest.com/v5/pins",
                json=payload,
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            )
            if resp.status_code in (200, 201):
                pid = resp.json().get("id", "")
                return SocialPostResult(platform="pinterest", success=True, post_id=pid)
            return SocialPostResult(platform="pinterest", success=False, error=f"Pinterest API {resp.status_code}: {resp.text[:200]}")
    except Exception as e:
        return SocialPostResult(platform="pinterest", success=False, error=str(e))


async def post_to_threads(req: SocialPostRequest) -> SocialPostResult:
    """Post to Threads via the Threads Graph API (credential-gated). Two-step: create container → publish."""
    token = settings.THREADS_ACCESS_TOKEN
    user_id = settings.THREADS_USER_ID
    if not token or not user_id:
        return SocialPostResult(platform="threads", success=False, error="Threads credentials not configured")

    caption = _build_caption(req, "threads")
    try:
        async with httpx.AsyncClient(timeout=25) as client:
            create = await client.post(
                f"https://graph.threads.net/v1.0/{user_id}/threads",
                data={"media_type": "TEXT", "text": caption, "access_token": token},
            )
            cdata = create.json()
            if "id" not in cdata:
                return SocialPostResult(platform="threads", success=False, error=str(cdata.get("error", cdata)))
            publish = await client.post(
                f"https://graph.threads.net/v1.0/{user_id}/threads_publish",
                data={"creation_id": cdata["id"], "access_token": token},
            )
            pdata = publish.json()
            if "id" in pdata:
                return SocialPostResult(platform="threads", success=True, post_id=pdata["id"])
            return SocialPostResult(platform="threads", success=False, error=str(pdata.get("error", pdata)))
    except Exception as e:
        return SocialPostResult(platform="threads", success=False, error=str(e))


async def post_to_gbp(req: SocialPostRequest) -> SocialPostResult:
    """Create a Google Business Profile local post (credential-gated)."""
    token = settings.GBP_ACCESS_TOKEN
    account_id = settings.GBP_ACCOUNT_ID
    location_id = settings.GBP_LOCATION_ID
    if not all([token, account_id, location_id]):
        return SocialPostResult(platform="gbp", success=False, error="Google Business Profile credentials not configured")

    payload = {
        "languageCode": "en-US",
        "summary": _build_caption(req, "gbp"),
        "callToAction": {"actionType": "LEARN_MORE", "url": req.post_url},
        "topicType": "STANDARD",
    }
    if req.image_url:
        payload["media"] = [{"mediaFormat": "PHOTO", "sourceUrl": req.image_url}]
    url = f"https://mybusiness.googleapis.com/v4/accounts/{account_id}/locations/{location_id}/localPosts"
    try:
        async with httpx.AsyncClient(timeout=25) as client:
            resp = await client.post(
                url, json=payload,
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            )
            if resp.status_code in (200, 201):
                name = resp.json().get("name", "")
                return SocialPostResult(platform="gbp", success=True, post_id=name)
            return SocialPostResult(platform="gbp", success=False, error=f"GBP API {resp.status_code}: {resp.text[:200]}")
    except Exception as e:
        return SocialPostResult(platform="gbp", success=False, error=str(e))


async def share_to_social(req: SocialPostRequest) -> List[SocialPostResult]:
    """Share a post to all requested platforms, each with a unique caption."""
    results = []
    handlers = {
        "facebook": post_to_facebook,
        "twitter": post_to_twitter,
        "x": post_to_twitter,
        "linkedin": post_to_linkedin,
        "instagram": post_to_instagram,
        "pinterest": post_to_pinterest,
        "threads": post_to_threads,
        "gbp": post_to_gbp,
    }
    for platform in req.platforms:
        handler = handlers.get(platform.lower())
        if handler:
            result = await handler(req)
            results.append(result)
        else:
            results.append(SocialPostResult(platform=platform, success=False, error=f"Unknown platform: {platform}"))
    return results
