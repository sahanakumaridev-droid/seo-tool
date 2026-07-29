# Zeorbit Revamp

Separate revamp project for `zeorbit.com` with:

- React frontend (`frontend`)
- Python FastAPI backend (`backend`)

## Frontend

```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

Frontend runs on `http://localhost:5173`.

## Backend

```bash
cd backend
cp .env.example .env
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Backend runs on `http://localhost:8000`.

## API Endpoints (starter)

- `GET /api/health`
- `POST /api/contact`

## Next Revamp Steps

1. Clone live `zeorbit.com` section-by-section into reusable React components.
2. Add routing for product, pricing, and contact pages.
3. Persist `contact` leads in a database and trigger email alerts.
4. Add auth and dashboard APIs for SEO tools.
