import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from routes import locations, content, pages, keywords, wordpress
from db import init_db

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(title="SEO Automation API", version="1.0.0")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "https://*.vercel.app",
        os.getenv("FRONTEND_URL", ""),
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    await init_db()

app.include_router(locations.router, prefix="/api/locations", tags=["Locations"])
app.include_router(content.router, prefix="/api/content", tags=["Content"])
app.include_router(pages.router, prefix="/api/pages", tags=["Pages"])
app.include_router(keywords.router, prefix="/api/keywords", tags=["Keywords"])
app.include_router(wordpress.router, prefix="/api/wordpress", tags=["WordPress"])

@app.get("/")
async def root():
    return {"status": "ok", "message": "SEO Automation API running"}
