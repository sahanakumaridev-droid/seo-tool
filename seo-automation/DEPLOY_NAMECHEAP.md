# Deploy to Namecheap (WordPress + SEO App) — Free-API Setup

This guide deploys the whole thing on Namecheap: your **WordPress blog** (publish target) and the **SEO app** (FastAPI backend + React frontend). It uses **free APIs** — a free LLM (Groq or Gemini) for content and free image sources — so there is no required paid key.

```
Browser ──> React frontend (public_html)  ──HTTPS──>  FastAPI backend (Python App)
                                                          │
                                                          └── publishes posts (REST + App Password) ──> WordPress
```

---

## 0. What you need
- Namecheap hosting with **cPanel** (shared/Stellar) **or** a Namecheap **VPS**.
- Your WordPress site (on Namecheap).
- One free LLM key: **Groq** (https://console.groq.com/keys) or **Gemini** (https://aistudio.google.com/app/apikey). Groq recommended (fast + generous free tier).

---

## 1. Prepare WordPress (the publish target)
1. Log into WP Admin → **Users → Profile → Application Passwords**. Create one named `seo-app`. Copy the value (looks like `xxxx xxxx xxxx xxxx`). This is `WP_APP_PASSWORD` — *not* your login password.
2. Install an SEO plugin: **Rank Math** (recommended), All in One SEO, or Yoast. Match it to `WP_SEO_PLUGIN`.
3. Confirm the REST API works: open `https://YOURSITE.com/wp-json/wp/v2/posts` in the browser — it should return JSON.
4. (Optional, if custom SEO meta doesn't stick) install a small mu-plugin to `register_meta` the `rank_math_*` keys, or rely on the plugin's own storage.

> Publishing sends: title, HTML content, slug, **featured image (WebP) + in-content images**, categories/tags, meta title/description, and Rank Math/AIOSEO/Yoast fields. The response `link` is the **live post URL** — that's what opens in your browser.

---

## 2. Backend (FastAPI) on cPanel — "Setup Python App"
cPanel Python apps run under **Passenger (WSGI)**; FastAPI is ASGI, so the repo includes `backend/passenger_wsgi.py` (wraps the app via `a2wsgi`).

1. cPanel → **Setup Python App** → **Create Application**:
   - Python version: 3.10+ (3.11/3.12 ideal).
   - Application root: e.g. `seo-backend`.
   - Application URL: a subdomain like `api.yoursite.com` (create it in cPanel → Domains/Subdomains first).
   - Application startup file: `passenger_wsgi.py` · Entry point: `application`.
2. Upload the `backend/` folder contents into the application root (File Manager or Git). Include `data/us_cities.json`.
3. In the Python App screen, add **Environment variables** (see section 4), then **Run pip install**:
   - Enter `requirements.txt` in "Configuration files" and click **Run Pip Install** (or open the app's virtualenv terminal and run `pip install -r requirements.txt`).
4. Click **Restart**. Test: `https://api.yoursite.com/health` → `{"status":"healthy"}`. Swagger: `https://api.yoursite.com/docs`.

> **Database**: defaults to SQLite (`seo_automation.db`) which is created automatically on first boot — fine for a single app. For higher traffic, create a MySQL/Postgres DB in cPanel and set `DATABASE_URL` (Postgres async: `postgresql+asyncpg://...`).

### Alternative: Namecheap VPS
```bash
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000        # test
# production: run under systemd + Nginx reverse proxy on api.yoursite.com (SSL via Let's Encrypt)
```

---

## 3. Frontend (React) on cPanel
1. On your machine, set the API base and build:
   ```bash
   cd frontend
   echo "VITE_API_URL=https://api.yoursite.com/api" > .env.production
   npm install && npm run build
   ```
2. Upload everything in `frontend/dist/` to the web root that serves the app (e.g. `public_html/` for the main domain, or the subdomain's folder).
3. Add SPA routing — create `.htaccess` next to `index.html`:
   ```apache
   <IfModule mod_rewrite.c>
     RewriteEngine On
     RewriteBase /
     RewriteRule ^index\.html$ - [L]
     RewriteCond %{REQUEST_FILENAME} !-f
     RewriteCond %{REQUEST_FILENAME} !-d
     RewriteRule . /index.html [L]
   </IfModule>
   ```

---

## 4. Backend environment variables (set in the Python App / VPS)
```
# Free LLM (pick one) — content works without it via the template engine, but a key gives unique articles
GROQ_API_KEY=gsk_...            # or:
GEMINI_API_KEY=...
LLM_PROVIDER=auto

# WordPress publish target
WP_URL=https://yoursite.com
WP_USERNAME=your_wp_login
WP_APP_PASSWORD=xxxx xxxx xxxx xxxx
WP_SEO_PLUGIN=rankmath

# Let the backend accept requests from the frontend (CORS)
FRONTEND_URL=https://yoursite.com

# Optional (all free tiers; safe to leave blank)
GOOGLE_PLACES_API_KEY=          # enables lead prospecting
UNSPLASH_ACCESS_KEY=            # nicer images; picsum fallback works with none
PEXELS_API_KEY=
DATABASE_URL=sqlite+aiosqlite:///./seo_automation.db
```
> After changing env vars, **Restart** the Python App.

---

## 5. End-to-end test (the "publish a blog like Chrome" flow)
1. Open the app (frontend URL) → **Articles**.
2. Enter a **primary keyword**, a **US location** (e.g. `Austin, TX`), your **website URL**, and set the **Nearby US Cities** slider (e.g. 5). Click **Generate Articles** → you get one localized post per city, each with a featured image.
3. Open the **WordPress Auto-Publish** panel, enter `WP_URL` + username + App Password, choose **publish**.
4. Publish **one** post (row → **Publish**) or **all** (**Publish All to WordPress**).
5. On success the row shows **Open Live** → click it → the published post opens live in your browser. That link is a real, shareable WordPress URL.

Single vs bulk:
- **Single blog post**: the per-row **Publish** button, or the **Publish to WordPress** button on the article's **View** (preview) screen.
- **All posts**: **Publish All to WordPress**.

---

## 6. Troubleshooting
- **502 "generation failed"** → set `GROQ_API_KEY` (or `GEMINI_API_KEY`); without a key it uses the free template engine (still works, less unique).
- **CORS error in browser console** → `FRONTEND_URL` must exactly match your frontend origin; Restart the app.
- **WP publish 401/403** → wrong Application Password, or the user lacks author rights. Regenerate the App Password.
- **Featured image missing on WP** → the source image URL must be publicly reachable; check the app can fetch it (outbound HTTP allowed on your host).
- **Passenger 500** → check the app's `stderr.log` in cPanel; usually a missing pip dependency — rerun pip install in the app's virtualenv.
