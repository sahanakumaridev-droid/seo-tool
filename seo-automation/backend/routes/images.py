from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.image_service import get_image_for_content, generate_dalle_image
import base64, httpx

router = APIRouter()

class ImageRequest(BaseModel):
    business_type: str
    city: str
    prompt: str = ""

@router.post("/generate")
async def generate_image(req: ImageRequest):
    """
    Generate or fetch a relevant image for a business/city.
    Returns a hosted URL (Unsplash/Pexels) or a base64 data URL (DALL-E).
    Priority: Unsplash → Pexels → DALL-E 3
    """
    result = await get_image_for_content(req.business_type, req.city)

    if result:
        img_bytes, filename = result
        # If it's from Unsplash/Pexels we have raw bytes — convert to data URL
        ext = "png" if filename.endswith(".png") else "jpeg"
        b64 = base64.b64encode(img_bytes).decode()
        data_url = f"data:image/{ext};base64,{b64}"
        return {"image_url": data_url, "filename": filename, "source": "auto"}

    raise HTTPException(
        status_code=503,
        detail="No image API configured. Add UNSPLASH_ACCESS_KEY, PEXELS_API_KEY, or OPENAI_API_KEY to .env"
    )

@router.post("/generate/dalle")
async def generate_dalle(req: ImageRequest):
    """Force DALL-E 3 image generation."""
    prompt = req.prompt or f"Professional {req.business_type} service in {req.city}, modern, clean, no text overlays"
    result = await generate_dalle_image(prompt)
    if result:
        img_bytes, filename = result
        b64 = base64.b64encode(img_bytes).decode()
        return {"image_url": f"data:image/png;base64,{b64}", "filename": filename, "source": "dalle"}
    raise HTTPException(status_code=503, detail="DALL-E generation failed. Check OPENAI_API_KEY in .env")
