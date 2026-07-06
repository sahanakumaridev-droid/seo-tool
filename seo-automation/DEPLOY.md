# Free Deployment Guide — ZEORBIT SEO Tool

## Stack
| Service | Platform | Cost |
|---------|----------|------|
| Frontend | Vercel | Free forever |
| Backend API | Render | Free (750 hrs/month) |
| Database | Render PostgreSQL | Free (90 days) or Supabase (free forever) |

---

## Step 1 — Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/zeorbit-seo.git
git push -u origin main
```

---

## Step 2 — Deploy Backend on Render (Free)

1. Go to **https://render.com** → Sign up free
2. Click **New → Web Service**
3. Connect your GitHub repo
4. Set these settings:
   - **Root Directory:** `seo-automation/backend`
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Plan:** Free

5. Add **Environment Variables** in Render dashboard:
   ```
   DATABASE_URL        = (from Render PostgreSQL — see Step 3)
   OPENAI_API_KEY      = sk-...
   FRONTEND_URL        = https://your-app.vercel.app
   UNSPLASH_ACCESS_KEY = (optional)
   PEXELS_API_KEY      = (optional)
   ```

6. Click **Deploy** — your backend URL will be:
   `https://zeorbit-backend.onrender.com`

> ⚠️ Free Render services sleep after 15 min of inactivity. First request takes ~30s to wake up.

---

## Step 3 — Free Database

### Option A: Render PostgreSQL (Free 90 days)
1. In Render → **New → PostgreSQL**
2. Name: `zeorbit-db`, Plan: **Free**
3. Copy the **Internal Database URL**
4. Paste it as `DATABASE_URL` in your backend service env vars

### Option B: Supabase (Free forever — recommended)
1. Go to **https://supabase.com** → New project
2. Settings → Database → Copy **Connection string (URI)**
3. Replace `postgresql://` with `postgresql+asyncpg://`
4. Paste as `DATABASE_URL` in Render env vars

---

## Step 4 — Deploy Frontend on Vercel (Free)

1. Go to **https://vercel.com** → Sign up free
2. Click **Add New → Project**
3. Import your GitHub repo
4. Set **Root Directory:** `seo-automation/frontend`
5. Framework: **Vite** (auto-detected)
6. Add **Environment Variable:**
   ```
   VITE_API_URL = https://zeorbit-backend.onrender.com/api
   ```
7. Click **Deploy** — your app URL will be:
   `https://zeorbit-seo.vercel.app`

---

## Step 5 — Update Backend CORS

After getting your Vercel URL, update Render env var:
```
FRONTEND_URL = https://zeorbit-seo.vercel.app
```

---

## Step 6 — Update vercel.json with your Render URL

Edit `seo-automation/frontend/vercel.json`:
```json
{
  "rewrites": [
    { "source": "/api/:path*", "destination": "https://YOUR-RENDER-URL.onrender.com/api/:path*" },
    { "source": "/(.*)", "destination": "/index.html" }
  ]
}
```

---

## Free Tier Limits

| Service | Limit |
|---------|-------|
| Vercel | 100GB bandwidth/month, unlimited deploys |
| Render Web | 750 hrs/month (enough for 1 service 24/7) |
| Render PostgreSQL | 1GB storage, 90 days free |
| Supabase | 500MB DB, 2GB bandwidth/month |
| OpenAI | Pay per use (~$0.01/page with GPT-4o-mini) |
| Unsplash | 50 requests/hour free |
| Pexels | 200 requests/hour free |

---

## Alternative: Railway (Easiest, $5 free credit)

1. Go to **https://railway.app**
2. New Project → Deploy from GitHub
3. Add both `backend` and `frontend` services
4. Railway auto-detects Python + Node
5. Add a PostgreSQL plugin
6. Set env vars and deploy

Railway gives $5 free credit/month which covers small projects indefinitely.
