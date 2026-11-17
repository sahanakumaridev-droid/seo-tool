"""Give today's repeated dental stock photos a unique image each."""
import json
import re
import sqlite3
import sys

sys.path.insert(0, "/opt/seo-tool/backend")
from services.image_service import (  # noqa: E402
    _all_curated_urls,
    _is_banned_stock_key,
    _with_unsplash_params,
    normalize_image_key,
)

REPEATED = ("1629909613654", "1606811841689", "1588776814546")
DB = "/opt/seo-tool/backend/seo_automation.db"


def pool() -> list[str]:
    seen = set()
    urls = []
    for url in _all_curated_urls():
        key = normalize_image_key(url)
        if not key or key in seen or _is_banned_stock_key(key):
            continue
        if any(token in url for token in REPEATED):
            continue
        seen.add(key)
        urls.append(_with_unsplash_params(url))
    return urls


def main() -> None:
    images = pool()
    print("pool", len(images))
    con = sqlite3.connect(DB)
    rows = con.execute(
        "SELECT id, seo_block FROM pages WHERE created_at >= ?",
        ("2026-10-30",),
    ).fetchall()
    cursor = 0
    changed = 0
    used = []
    for page_id, raw in rows:
        data = json.loads(raw)
        html = data.get("content_html") or ""
        image_url = data.get("image_url") or ""
        if not any(token in html or token in image_url for token in REPEATED):
            continue
        found = re.findall(r'src="(https://images\.unsplash\.com/[^"]+)"', html)
        replacements = []
        for _ in found:
            replacements.append(images[cursor % len(images)])
            cursor += 1
        step = {"i": 0}

        def repl(match, replacements=replacements, step=step):
            url = replacements[step["i"]]
            step["i"] += 1
            return f'src="{url}"'

        data["content_html"] = re.sub(
            r'src="https://images\.unsplash\.com/[^"]+"',
            repl,
            html,
        )
        if replacements:
            data["image_url"] = replacements[0]
            used.extend(replacements)
        con.execute(
            "UPDATE pages SET seo_block=? WHERE id=?",
            (json.dumps(data), page_id),
        )
        changed += 1
    con.commit()
    with open("/opt/seo-tool/backend/routes/used_blog_images.json", "w") as handle:
        json.dump(used[-4000:], handle)

    still = 0
    within = 0
    keys = []
    for _, raw in con.execute(
        "SELECT id, seo_block FROM pages WHERE created_at >= ?",
        ("2026-10-30",),
    ):
        data = json.loads(raw)
        html = data.get("content_html") or ""
        if any(token in html for token in REPEATED):
            still += 1
        imgs = [
            url.split("?")[0]
            for url in re.findall(r'src="(https://images\.unsplash\.com/[^"]+)"', html)
        ]
        if len(imgs) != len(set(imgs)):
            within += 1
        keys.extend(imgs)
    print(
        "rewritten", changed,
        "slots", cursor,
        "still_dental", still,
        "within_dupes", within,
        "unique_photos", len(set(keys)),
        "image_slots", len(keys),
    )


if __name__ == "__main__":
    main()
