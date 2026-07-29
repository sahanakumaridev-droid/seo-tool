# Deploy ZeOrbit Website as a VPS sibling of SEO Tool

## Live (deployed)

| Item | Path / URL |
|------|------------|
| SEO Tool (existing) | `/var/www/seo-tool` + `/opt/seo-tool` |
| Website (sibling) | `/var/www/zeorbit-website` |
| Website URL | https://zeorbit.159.198.79.219.nip.io |
| Blog | https://zeorbit.159.198.79.219.nip.io/blog |
| SEO Tool URL | https://seo.159.198.79.219.nip.io |
| Backend | `127.0.0.1:8001` (`seo-tool.service`) |
| SSH | `ssh zedev` → `159.198.79.219` |

## Redeploy website

```bash
cd zeorbit-website
VITE_API_URL=/api ./scripts/build.sh
rsync -avz --delete dist/ zedev:/var/www/zeorbit-website/
```

## Redeploy blog API (backend)

```bash
scp seo-automation/backend/routes/pages.py zedev:/opt/seo-tool/backend/routes/pages.py
ssh zedev 'systemctl restart seo-tool.service'
```
