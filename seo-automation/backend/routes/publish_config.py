"""Custom Plugin tab: save ZeOrbit, WordPress, and Shopify server details."""
import httpx
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from auth import get_current_active_user
from services.publish_config import public_view, save_public

router = APIRouter()


class PublishServersIn(BaseModel):
    zeorbit_url: str = ""
    wp_url: str = ""
    wp_username: str = ""
    wp_app_password: str = ""
    wp_seo_plugin: str = "rankmath"
    shopify_store: str = ""
    shopify_access_token: str = ""
    shopify_blog_id: str = ""


@router.get("")
async def read_servers(_user=Depends(get_current_active_user)):
    return public_view()


@router.put("")
async def write_servers(body: PublishServersIn, _user=Depends(get_current_active_user)):
    saved = save_public(body.model_dump())
    checks = await _checks()
    return {**saved, "checks": checks}


@router.post("/test")
async def test_servers(_user=Depends(get_current_active_user)):
    return {"checks": await _checks()}


async def _checks() -> dict:
    view = public_view()
    from config import settings

    zeorbit = {"ok": bool(view["zeorbit_ready"]), "detail": view["zeorbit_url"] or "Add the ZeOrbit site URL."}
    wordpress = {"ok": False, "detail": "Add the WordPress URL, username, and application password."}
    shopify = {"ok": False, "detail": "Add the Shopify store and access token."}
    async with httpx.AsyncClient(timeout=12, follow_redirects=True) as client:
        if view["wordpress_ready"]:
            try:
                res = await client.get(
                    f"{settings.WP_URL.rstrip('/')}/wp-json/wp/v2/users/me",
                    auth=(settings.WP_USERNAME, settings.WP_APP_PASSWORD),
                )
                wordpress = {
                    "ok": res.status_code < 400,
                    "detail": "WordPress accepted the login." if res.status_code < 400 else "WordPress refused the username or application password.",
                }
            except httpx.HTTPError:
                wordpress = {"ok": False, "detail": "The WordPress site did not respond."}
        if view["shopify_ready"]:
            store = settings.SHOPIFY_STORE.strip().rstrip("/")
            try:
                res = await client.get(
                    f"https://{store}/admin/api/2024-10/shop.json",
                    headers={"X-Shopify-Access-Token": settings.SHOPIFY_ACCESS_TOKEN},
                )
                shopify = {
                    "ok": res.status_code < 400,
                    "detail": "Shopify accepted the token." if res.status_code < 400 else "Shopify refused the store or access token.",
                }
            except httpx.HTTPError:
                shopify = {"ok": False, "detail": "The Shopify store did not respond."}
    return {"zeorbit": zeorbit, "wordpress": wordpress, "shopify": shopify}
