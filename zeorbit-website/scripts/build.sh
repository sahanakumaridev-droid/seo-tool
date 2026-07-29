#!/usr/bin/env bash
# Build this website for production (sibling deploy next to SEO Tool)
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

API_URL="${VITE_API_URL:-/api}"
echo "Building zeorbit-website with VITE_API_URL=$API_URL"

npm install --silent
VITE_API_URL="$API_URL" npm run build

# SPA fallback for Apache
cat > dist/.htaccess <<'EOF'
<IfModule mod_rewrite.c>
  RewriteEngine On
  RewriteBase /
  RewriteRule ^index\.html$ - [L]
  RewriteCond %{REQUEST_FILENAME} !-f
  RewriteCond %{REQUEST_FILENAME} !-d
  RewriteRule . /index.html [L]
</IfModule>
EOF

cp nginx.zeorbit-website.conf.example dist/nginx.zeorbit-website.conf.example

echo "Done → $ROOT/dist"
echo "Upload: rsync -avz --delete dist/ root@YOUR_VPS:/var/www/zeorbit-website/"
