# ZeOrbit Website (new sibling project)

Standalone marketing website for ZeOrbit. Lives next to `seo-automation/` (the SEO Tool).

```
SEO_Tool/
├── seo-automation/   ← SEO Tool (API, dashboard, publish)
└── zeorbit-website/  ← this site (landing, blog, services)
```

## Connects to SEO Tool

- Blog / Insights load from `GET /api/pages/blog`
- Live articles open at `/p/{slug}` (proxied to SEO Tool backend)

## Local development

```bash
# Terminal 1 — SEO Tool API (port 8000)
cd ../seo-automation/backend && uvicorn main:app --reload --port 8000

# Terminal 2 — this website (port 5180)
cd ../zeorbit-website && npm run dev
```

Open: **http://127.0.0.1:5180/**  
Blog: **http://127.0.0.1:5180/blog**

## Production build

```bash
export VITE_API_URL=https://YOUR-API-HOST/api   # or leave /api if Nginx proxies
./scripts/build.sh
```

See `DEPLOY_VPS.md` for VPS sibling deploy next to the SEO Tool.
