#!/usr/bin/env python3
"""
setup_gsc.py — one-time Google Search Console setup for ZeOrbit /p/ pages.

Goal: published SEO pages can be discovered & inspected by Google Search.

You must complete Google Cloud + Search Console steps in the browser (Google
requires your account). This script opens the right pages, waits for the
service-account JSON, writes .env, submits the sitemap, and bootstraps URLs.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENV_PATH = ROOT / ".env"
SECRETS = ROOT / "secrets"
KEY_PATH = SECRETS / "gsc-service-account.json"
PUBLIC_BASE = os.environ.get("PUBLIC_BASE_URL", "https://zeorbit.com")
GSC_SITE = "https://www.zeorbit.com/"
SITEMAP = "https://zeorbit.com/sitemap_index.xml"
PAGE_SITEMAP = "https://zeorbit.com/page-sitemap.xml"
POST_SITEMAP = "https://zeorbit.com/post-sitemap.xml"


def upsert_env(updates: dict[str, str]) -> None:
    text = ENV_PATH.read_text(encoding="utf-8") if ENV_PATH.exists() else ""
    for key, value in updates.items():
        pattern = re.compile(rf"^{re.escape(key)}=.*$", re.MULTILINE)
        line = f"{key}={value}"
        if pattern.search(text):
            text = pattern.sub(line, text)
        else:
            if text and not text.endswith("\n"):
                text += "\n"
            text += line + "\n"
    ENV_PATH.write_text(text, encoding="utf-8")


def open_url(url: str) -> None:
    try:
        subprocess.run(["/usr/bin/open", url], check=False)
    except Exception:
        print("OPEN:", url)


def main() -> int:
    SECRETS.mkdir(parents=True, exist_ok=True)
    upsert_env(
        {
            "GSC_SITE_URL": GSC_SITE,
            "WP_SITEMAP_URL": SITEMAP,
            "WP_PAGE_SITEMAP_URL": PAGE_SITEMAP,
            "WP_POST_SITEMAP_URL": POST_SITEMAP,
            "GOOGLE_INDEXING_KEY_FILE": str(KEY_PATH),
            "GSC_AUTO_PUSH_ON_PUBLISH": "true",
            "DEMO_MODE": "false",
        }
    )
    print("ENV written:")
    print("  GSC_SITE_URL    =", GSC_SITE)
    print("  KEY FILE        =", KEY_PATH)
    print()
    print("=== Do these steps in the browser (required once) ===")
    print("1) Enable Search Console API in Google Cloud")
    print("2) Create a service account → Keys → JSON → save as:")
    print(f"   {KEY_PATH}")
    print("3) Search Console → Add property → URL prefix:")
    print("   https://www.zeorbit.com/")
    print("   (or Domain property: zeorbit.com)")
    print("4) Verify (HTML tag or HTML file) — paste token into .env as")
    print("   GSC_VERIFICATION_META=... then restart backend")
    print("5) Settings → Users → add the service-account email as Owner")
    print()

    open_url("https://console.cloud.google.com/apis/library/searchconsole.googleapis.com")
    time.sleep(1)
    open_url("https://console.cloud.google.com/iam-admin/serviceaccounts")
    time.sleep(1)
    open_url("https://search.google.com/search-console")
    time.sleep(1)
    open_url(SITEMAP)

    print("Waiting up to 10 minutes for:", KEY_PATH)
    deadline = time.time() + 600
    while time.time() < deadline:
        if KEY_PATH.exists() and KEY_PATH.stat().st_size > 50:
            try:
                data = json.loads(KEY_PATH.read_text(encoding="utf-8"))
                email = data.get("client_email") or ""
                if not email.endswith(".iam.gserviceaccount.com"):
                    print("WARN: file found but client_email looks wrong:", email)
                else:
                    print("KEY OK — service account:", email)
                    print("Add that email as Owner in Search Console, then press Enter.")
                    try:
                        input()
                    except EOFError:
                        pass
                    # Validate API after reload settings
                    sys.path.insert(0, str(ROOT))
                    os.chdir(ROOT)
                    from importlib import reload
                    import config as config_mod
                    reload(config_mod)
                    from services import search_console_service as sc

                    sc._loaded = False
                    sc._session = None
                    if not sc.is_configured():
                        print("FAIL: Search Console still not configured — check key path + GSC_SITE_URL")
                        return 1
                    for sm in (SITEMAP, PAGE_SITEMAP, POST_SITEMAP):
                        result = sc.submit_sitemap(sm)
                        print("SITEMAP_SUBMIT:", sm, result)
                    print("SUCCESS: GSC wired to www.zeorbit.com. Restart backend, open Google Indexing, click Push all.")
                    return 0
            except Exception as e:
                print("KEY parse error:", e)
        time.sleep(2)

    print("TIMEOUT: drop the JSON key at", KEY_PATH, "and re-run this script.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
