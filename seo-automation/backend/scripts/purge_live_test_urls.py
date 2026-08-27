#!/usr/bin/env python3
"""Purge SEO-tool test URLs from the live ZeOrbit site.

- Backs up the DB
- Deletes pages + published_urls
- Writes an nginx map of purged slugs for 410 Gone
"""
from __future__ import annotations

import shutil
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "seo_automation.db"
MAP_PATH = Path("/etc/nginx/snippets/zeorbit-seo-test-gone.map")
SLUG_LOG_DIR = Path("/root")


def main() -> None:
    if not DB_PATH.exists():
        raise SystemExit(f"DB not found: {DB_PATH}")

    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    backup = DB_PATH.with_name(f"seo_automation.backup-pre-purge-{stamp}.db")
    shutil.copy2(DB_PATH, backup)
    print(f"Backup → {backup}")

    conn = sqlite3.connect(str(DB_PATH))
    slugs = [
        r[0]
        for r in conn.execute(
            "SELECT slug FROM pages WHERE slug IS NOT NULL AND TRIM(slug) != ''"
        ).fetchall()
    ]
    pub_urls = [r[0] for r in conn.execute("SELECT url FROM published_urls").fetchall()]
    print(f"pages={len(slugs)} published_urls={len(pub_urls)}")

    for u in pub_urls:
        path = (urlparse(u or "").path or "").strip("/")
        if path and "/" not in path:
            slugs.append(path)

    slugs = sorted({(s or "").strip("/").lower() for s in slugs if s})

    lines = [
        "# Auto-generated purged SEO-tool test URLs -> 410",
        "map $uri $zeorbit_seo_test_gone {",
        "    default 0;",
    ]
    for s in slugs:
        lines.append(f"    /{s} 1;")
        lines.append(f"    /{s}/ 1;")
    lines.append("}")
    MAP_PATH.parent.mkdir(parents=True, exist_ok=True)
    MAP_PATH.write_text("\n".join(lines) + "\n")
    print(f"Wrote nginx map ({len(slugs)} slugs) → {MAP_PATH}")

    SLUG_LOG_DIR.mkdir(parents=True, exist_ok=True)
    log = SLUG_LOG_DIR / f"purged-seo-slugs-{stamp}.txt"
    log.write_text("\n".join(slugs) + "\n")
    print(f"Slug log → {log}")

    conn.execute("DELETE FROM pages")
    conn.execute("DELETE FROM published_urls")
    conn.commit()
    print(
        "DB purged: pages=",
        conn.execute("SELECT COUNT(*) FROM pages").fetchone()[0],
        "published_urls=",
        conn.execute("SELECT COUNT(*) FROM published_urls").fetchone()[0],
    )
    conn.close()
    print("Done.")


if __name__ == "__main__":
    main()
