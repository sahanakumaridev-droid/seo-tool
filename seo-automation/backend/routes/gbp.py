from fastapi import APIRouter
from models.schemas import GBPPostRequest, GBPPostResult, GBPSuggestRequest
from services.social_service import post_gbp_update, gbp_configured
from providers.demo_google import use_demo_fallback, free_gbp_message
from services.llm_service import chat_text, active_provider, llm_available

router = APIRouter()


@router.get("/status")
async def get_status():
    live = gbp_configured()
    demo = use_demo_fallback(live)
    llm = active_provider() if llm_available() else None
    if live:
        mode = "live"  # free Google Business Profile API
    elif llm:
        mode = "ai"    # free Groq/Gemini drafts; connect GBP to publish
    elif demo:
        mode = "demo"
    else:
        mode = "setup"
    return {
        "configured": live or demo,
        "demo": demo,
        "live": live,
        "llm_provider": llm,
        "mode": mode,
    }


@router.post("/post", response_model=GBPPostResult)
async def create_post(req: GBPPostRequest):
    return await post_gbp_update(req)


@router.post("/suggest")
async def suggest_post(req: GBPSuggestRequest):
    """Free AI draft (Groq/Gemini) or template — no paid APIs."""
    prompt = (
        f"Write a short Google Business Profile update (max 280 characters) for "
        f"{req.business_name or 'a local business'} in {req.city or 'their city'} "
        f"about {req.service or 'their services'}. Tone: {req.tone}. "
        f"No hashtags. No emojis. Include a clear call to action."
    )
    provider = active_provider()
    try:
        text = await chat_text(prompt, temperature=0.7, max_tokens=200)
        if text and text.strip():
            return {
                "message": text.strip()[:1500],
                "demo": False,
                "source": "ai",
                "provider": provider,
            }
    except Exception:
        pass
    return {
        "message": free_gbp_message(req.business_name, req.city, req.service),
        "demo": False,
        "source": "template",
        "provider": None,
    }
