#!/usr/bin/env python3
"""
purge_test_seo_content.py — remove all SEO-tool pages + indexing rows so Google
stops discovering test URLs. Keeps users/leads/marketplace tables.

Usage (on the VPS, from backend/):
  ./venv/bin/python3 scripts/purge_test_seo_content.py
"""
from __future__ import annotations

import shutil
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import create_engine, text

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "seo_automation.db"


def main() -> None:
    if not DB_PATH.exists():
        raise SystemExit(f"DB not found: {DB_PATH}")

    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    backup = DB_PATH.with_name(f"seo_automation.backup-pre-purge-{stamp}.db")
    shutil.copy2(DB_PATH, backup)
    print(f"Backup → {backup}")

    engine = create_engine(f"sqlite:///{DB_PATH}")
    with engine.begin() as conn:
        pages = conn.execute(text("SELECT COUNT(*) FROM pages")).scalar() or 0
        pubs = conn.execute(text("SELECT COUNT(*) FROM published_urls")).scalar() or 0
        conn.execute(text("DELETE FROM pages"))
        conn.execute(text("DELETE FROM published_urls"))
        print(f"Deleted pages={pages} published_urls={pubs}")

    print("Done. Restart seo-tool.service, then ping Google with the new sitemaps.")


if __name__ == "__main__":
    main()
