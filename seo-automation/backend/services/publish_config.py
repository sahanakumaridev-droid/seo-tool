"""Saved publish servers. The Custom Plugin tab writes this file; startup applies it."""
import json
from pathlib import Path

from config import settings

_PATH = Path(__file__).resolve().parent.parent / "data" / "publish_targets.json"

_FIELDS = (
    "zeorbit_url",
    "wp_url",
    "wp_username",
    "wp_app_password",
    "wp_seo_plugin",
    "shopify_store",
    "shopify_access_token",
    "shopify_blog_id",
)


def _clean(value) -> str:
    return str(value or "").strip()


def _current() -> dict:
    return {
        "zeorbit_url": _clean(settings.MARKETING_SITE_URL) or "https://zeorbit.com",
        "wp_url": _clean(settings.WP_URL),
        "wp_username": _clean(settings.WP_USERNAME),
        "wp_app_password": _clean(settings.WP_APP_PASSWORD),
        "wp_seo_plugin": _clean(settings.WP_SEO_PLUGIN) or "rankmath",
        "shopify_store": _clean(settings.SHOPIFY_STORE),
        "shopify_access_token": _clean(settings.SHOPIFY_ACCESS_TOKEN),
        "shopify_blog_id": _clean(settings.SHOPIFY_BLOG_ID),
    }


def _read() -> dict | None:
    if not _PATH.exists():
        return None
    try:
        data = json.loads(_PATH.read_text())
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(data, dict):
        return None
    return {key: _clean(data.get(key)) for key in _FIELDS}


def apply_saved() -> None:
    """Load the saved file over the process settings. Env values stay until a save exists."""
    saved = _read()
    if not saved:
        return
    _apply(saved)


def _apply(data: dict) -> None:
    settings.MARKETING_SITE_URL = data["zeorbit_url"] or "https://zeorbit.com"
    settings.WP_URL = data["wp_url"]
    settings.WP_USERNAME = data["wp_username"]
    settings.WP_APP_PASSWORD = data["wp_app_password"]
    settings.WP_SEO_PLUGIN = data["wp_seo_plugin"] or "rankmath"
    settings.SHOPIFY_STORE = data["shopify_store"]
    settings.SHOPIFY_ACCESS_TOKEN = data["shopify_access_token"]
    settings.SHOPIFY_BLOG_ID = data["shopify_blog_id"]


def public_view() -> dict:
    data = _read() or _current()
    return {
        "zeorbit_url": data["zeorbit_url"],
        "wp_url": data["wp_url"],
        "wp_username": data["wp_username"],
        "wp_password_set": bool(data["wp_app_password"]),
        "wp_seo_plugin": data["wp_seo_plugin"] or "rankmath",
        "shopify_store": data["shopify_store"],
        "shopify_token_set": bool(data["shopify_access_token"]),
        "shopify_blog_id": data["shopify_blog_id"],
        "zeorbit_ready": bool(data["zeorbit_url"]),
        "wordpress_ready": bool(data["wp_url"] and data["wp_username"] and data["wp_app_password"]),
        "shopify_ready": bool(data["shopify_store"] and data["shopify_access_token"]),
    }


def save_public(incoming: dict) -> dict:
    current = _read() or _current()
    merged = dict(current)
    for key in ("zeorbit_url", "wp_url", "wp_username", "wp_seo_plugin", "shopify_store", "shopify_blog_id"):
        if key in incoming and incoming[key] is not None:
            merged[key] = _clean(incoming[key])
    password = _clean(incoming.get("wp_app_password"))
    if password:
        merged["wp_app_password"] = password
    token = _clean(incoming.get("shopify_access_token"))
    if token:
        merged["shopify_access_token"] = token
    if not merged["wp_seo_plugin"]:
        merged["wp_seo_plugin"] = "rankmath"
    if merged["zeorbit_url"] and not merged["zeorbit_url"].startswith(("http://", "https://")):
        merged["zeorbit_url"] = f"https://{merged['zeorbit_url']}"
    if merged["wp_url"]:
        merged["wp_url"] = merged["wp_url"].rstrip("/")
        if not merged["wp_url"].startswith(("http://", "https://")):
            merged["wp_url"] = f"https://{merged['wp_url']}"
    store = merged["shopify_store"]
    for prefix in ("https://", "http://"):
        if store.startswith(prefix):
            store = store[len(prefix):]
    merged["shopify_store"] = store.strip("/")
    _PATH.parent.mkdir(parents=True, exist_ok=True)
    _PATH.write_text(json.dumps({key: merged[key] for key in _FIELDS}, indent=2) + "\n")
    _apply(merged)
    _sync_env(merged)
    return public_view()


def _sync_env(data: dict) -> None:
    """Keep the server .env in step so a restart still has these servers."""
    env_path = Path(__file__).resolve().parent.parent / ".env"
    if not env_path.exists():
        return
    mapping = {
        "WP_URL": data["wp_url"],
        "WP_USERNAME": data["wp_username"],
        "WP_APP_PASSWORD": data["wp_app_password"],
        "WP_SEO_PLUGIN": data["wp_seo_plugin"],
        "SHOPIFY_STORE": data["shopify_store"],
        "SHOPIFY_ACCESS_TOKEN": data["shopify_access_token"],
        "SHOPIFY_BLOG_ID": data["shopify_blog_id"],
        "MARKETING_SITE_URL": data["zeorbit_url"],
    }
    lines = env_path.read_text().splitlines()
    seen = set()
    out = []
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in line:
            out.append(line)
            continue
        key = line.split("=", 1)[0].strip()
        if key in mapping:
            out.append(f"{key}={_env_value(mapping[key])}")
            seen.add(key)
        else:
            out.append(line)
    if seen != set(mapping):
        out.append("")
        for key, value in mapping.items():
            if key not in seen:
                out.append(f"{key}={_env_value(value)}")
    env_path.write_text("\n".join(out).rstrip() + "\n")


def _env_value(value: str) -> str:
    if any(ch in value for ch in (" ", "#", '"')):
        return '"' + value.replace('"', '\\"') + '"'
    return value
