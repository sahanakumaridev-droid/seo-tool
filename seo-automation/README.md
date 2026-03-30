# SEO Automation Tool

AI-powered local SEO content generator for 50+ cities.

## Quick Start

### Backend (Python/FastAPI)
```bash
cd backend
cp .env.example .env
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Frontend (React)
```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173

## Free APIs Used (No Key Required)
- **Datamuse** — keyword generation
- **Hardcoded SD city list** — 50 San Diego area cities with coordinates

## Optional API Keys (.env)
- `OPENCAGE_API_KEY` — geocode any base location (free tier: 2500 req/day)
  Get one at: https://opencagedata.com/

## API Endpoints
| Method | Path | Description |
|--------|------|-------------|
| POST | /api/content/generate | Bulk generate SEO pages |
| POST | /api/content/generate/single | Single city page |
| GET | /api/locations/nearby | Fetch nearby cities |
| GET | /api/keywords/generate | Generate keyword set |
| POST | /api/content/export/json | Export as JSON |
| POST | /api/content/export/html | Export as HTML |
| POST | /api/content/export/wordpress | Export WP-ready format |
| POST | /api/pages/save | Save page to MongoDB |
| GET | /api/pages/ | List saved pages |

## Phase 2 Upgrades
- Set `OPENAI_API_KEY` in `.env` and swap `content_service.py` to use GPT-4
- Set `GOOGLE_PLACES_API_KEY` for real nearby city discovery
- MongoDB Atlas for cloud persistence
