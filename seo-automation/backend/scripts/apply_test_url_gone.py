#!/usr/bin/env python3
"""Apply 410 Gone for purged/test ZeOrbit URLs and clean stale static sitemaps."""
from __future__ import annotations

import re
import shutil
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

SNIPPET = Path("/etc/nginx/snippets/zeorbit-redirects.conf")
SITE = Path("/etc/nginx/sites-enabled/zeorbit.com")
WWW = Path("/var/www/zeorbit-website")
BACKUP_DB = Path("/opt/seo-tool/backend/seo_automation.backup-pre-purge-20260824-055641.db")
BACKUP_DIR = Path("/root/nginx-backups")


def main() -> None:
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")

    text = SNIPPET.read_text()
    shutil.copy2(SNIPPET, BACKUP_DIR / f"zeorbit-redirects.bak-{stamp}")

    text2, n = re.subn(
        r"(location = /[a-z0-9][a-z0-9-]{2,}/? \{ )return 301 /blog;",
        r"\1return 410;",
        text,
    )
    print(f"converted blog redirects to 410: {n}")

    slugs: list[str] = []
    if BACKUP_DB.exists():
        db = sqlite3.connect(str(BACKUP_DB))
        slugs = [r[0] for r in db.execute("select slug from pages order by slug")]
    print(f"seo tool slugs: {len(slugs)}")

    existing = set(re.findall(r"location = (/[^\s{]+)", text2))
    extra = ["", "# Purged SEO-tool test pages → 410 Gone (do not soft-redirect)"]
    added = 0
    for slug in slugs + ["education-coronado"]:
        for path in (f"/{slug}", f"/{slug}/"):
            if path in existing or f"location = {path} " in text2:
                continue
            extra.append(f"location = {path} {{ return 410; }}")
            existing.add(path)
            added += 1

    marker = "# WP archives → homepage"
    if marker not in text2:
        raise SystemExit("marker missing in redirects snippet")
    text2 = text2.replace(marker, "\n".join(extra) + "\n\n" + marker, 1)
    SNIPPET.write_text(text2)
    print(f"added 410 locations: {added}")

    site = SITE.read_text()
    old = (
        '    location ~ "^/(?!(?:blog|contact|portfolio|mobile-apps|custom-software|'
        'seo-ppc|website-designing|revamp-preview|us-only|health)(?:/|$))'
        '([a-z0-9][a-z0-9-]{2,})$" {\n'
        "        include /etc/nginx/snippets/zeorbit-geo-gate.conf;\n"
        "        proxy_pass http://127.0.0.1:8001/$1$is_args$args;\n"
        "        proxy_http_version 1.1;\n"
        "        proxy_set_header Host $host;\n"
        "        proxy_set_header X-Real-IP $remote_addr;\n"
        "        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;\n"
        "        proxy_set_header X-Forwarded-Proto $scheme;\n"
        '        add_header Cache-Control "no-store, no-cache, must-revalidate, max-age=0" always;\n'
        "    }"
    )
    new = (
        "    # Optional trailing slash; missing/tool-purged articles return 404/410.\n"
        '    location ~ "^/(?!(?:blog|contact|portfolio|mobile-apps|custom-software|'
        'seo-ppc|website-designing|revamp-preview|us-only|health)(?:/|$))'
        '([a-z0-9][a-z0-9-]{2,})/?$" {\n'
        "        include /etc/nginx/snippets/zeorbit-geo-gate.conf;\n"
        "        proxy_pass http://127.0.0.1:8001/$1$is_args$args;\n"
        "        proxy_http_version 1.1;\n"
        "        proxy_set_header Host $host;\n"
        "        proxy_set_header X-Real-IP $remote_addr;\n"
        "        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;\n"
        "        proxy_set_header X-Forwarded-Proto $scheme;\n"
        '        add_header Cache-Control "no-store, no-cache, must-revalidate, max-age=0" always;\n'
        "    }"
    )
    if old not in site:
        raise SystemExit("article location block not found in zeorbit.com")
    shutil.copy2(SITE, BACKUP_DIR / f"zeorbit.com.bak-{stamp}")
    SITE.write_text(site.replace(old, new, 1))
    print("zeorbit.com article regex updated")

    empty = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"></urlset>\n'
    )
    menu = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        "<url><loc>https://zeorbit.com</loc></url>"
        "<url><loc>https://zeorbit.com/website-designing</loc></url>"
        "<url><loc>https://zeorbit.com/mobile-apps</loc></url>"
        "<url><loc>https://zeorbit.com/seo-ppc</loc></url>"
        "<url><loc>https://zeorbit.com/custom-software</loc></url>"
        "<url><loc>https://zeorbit.com/portfolio</loc></url>"
        "<url><loc>https://zeorbit.com/contact</loc></url>"
        "<url><loc>https://zeorbit.com/blog</loc></url>"
        "</urlset>\n"
    )
    for name in ("post-sitemap.xml", "page-sitemap.xml"):
        p = WWW / name
        if p.exists() and not p.name.endswith(".bak-stale"):
            p.rename(WWW / f"{name}.bak-stale-{stamp}")
            print("backed up", name)
    (WWW / "post-sitemap.xml").write_text(empty)
    (WWW / "page-sitemap.xml").write_text(menu)
    print("static sitemaps replaced")


if __name__ == "__main__":
    main()
