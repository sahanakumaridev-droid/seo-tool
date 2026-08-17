#!/usr/bin/env bash
# Build this website for production (sibling deploy next to SEO Tool)
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

API_URL="${VITE_API_URL:-/api}"
echo "Building zeorbit-website with VITE_API_URL=$API_URL"

npm install --silent
VITE_API_URL="$API_URL" npm run build

python3 - <<'PY'
from pathlib import Path
import re
root = Path(".")
nginx = (root / "nginx-redirects.conf").read_text()
rules = []
for loc, dest in re.findall(r"location = (/[^\s{]+) \{ return 301 ([^;]+); \}", nginx):
    slug = loc.strip("/")
    if not slug:
        continue
    rules.append(f"  RewriteRule ^{re.escape(slug)}/?$ {dest} [R=301,L]")
for pattern, dest in re.findall(r"location ~ \^(/[^\s{]+) \{ return 301 ([^;]+); \}", nginx):
    rules.append(f"  RewriteRule ^{pattern.lstrip('/')} {dest} [R=301,L]")
htaccess = """<IfModule mod_rewrite.c>
  RewriteEngine On
  RewriteBase /
""" + "\n".join(rules) + """
  RewriteRule ^index\\.html$ - [L]
  RewriteCond %{REQUEST_FILENAME} !-f
  RewriteCond %{REQUEST_FILENAME} !-d
  RewriteRule . /index.html [L]
</IfModule>
"""
(root / "dist" / ".htaccess").write_text(htaccess)
print(f"Wrote dist/.htaccess with {len(rules)} 301 rules")
PY

cp nginx.zeorbit-website.conf.example dist/nginx.zeorbit-website.conf.example
cp nginx-redirects.conf dist/nginx-redirects.conf

echo "Done → $ROOT/dist"
echo "Upload: rsync -avz --delete dist/ root@YOUR_VPS:/var/www/zeorbit-website/"
