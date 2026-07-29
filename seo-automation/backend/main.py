import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse, PlainTextResponse, Response
from fastapi.staticfiles import StaticFiles
from db import get_session
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from routes import locations, content, pages, keywords, wordpress
from routes import social, leads, jobs, images, seo_audit, google_ads, gbp
from db import init_db
import db_marketplace  # registers marketplace ORM models with Base
from logging_config import setup_logging, logger
from config import settings
import uuid

# Setup logging
setup_logging()

limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown."""
    # Startup
    logger.info("Starting SEO Automation API v2.1")
    await init_db()
    logger.info("Database initialized")
    yield
    # Shutdown
    logger.info("Shutting down SEO Automation API")


app = FastAPI(
    title="SEO Automation API",
    version="2.1.0",
    description="AI-powered SEO automation with streaming, semantic search, and multi-model AI",
    lifespan=lifespan
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# ── Middleware ──────────────────────────────────────────────────
class RequestIDMiddleware:
    """Add request ID to all requests for tracing."""
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            request_id = str(uuid.uuid4())
            scope["request_id"] = request_id
            
            async def send_with_id(message):
                if message["type"] == "http.response.start":
                    headers = list(message.get("headers", []))
                    headers.append((b"x-request-id", request_id.encode()))
                    message["headers"] = headers
                await send(message)
            
            await self.app(scope, receive, send_with_id)
        else:
            await self.app(scope, receive, send)


app.add_middleware(RequestIDMiddleware)

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

# Serves brand assets (e.g. /static/zeorbit-logo.png) used in generated
# location pages, which are rendered server-side and can't reach into the
# frontend's own /public folder.
app.mount("/static", StaticFiles(directory="static"), name="static")


# ── Exception Handlers ──────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler with structured logging."""
    request_id = getattr(request.scope, "request_id", "unknown")
    logger.error(
        f"Unhandled exception",
        extra={
            "request_id": request_id,
            "path": request.url.path,
            "method": request.method,
            "error": str(exc)
        }
    )
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "request_id": request_id
        }
    )


# ── Routes ──────────────────────────────────────────────────────
# Core routes
app.include_router(locations.router, prefix="/api/locations", tags=["Locations"])
app.include_router(content.router,   prefix="/api/content",   tags=["Content"])
app.include_router(pages.router,     prefix="/api/pages",     tags=["Pages"])
app.include_router(keywords.router,  prefix="/api/keywords",  tags=["Keywords"])
app.include_router(wordpress.router, prefix="/api/wordpress", tags=["WordPress"])
app.include_router(social.router,    prefix="/api/social",    tags=["Social Media"])
app.include_router(leads.router,     prefix="/api/leads",     tags=["Leads"])
app.include_router(jobs.router,      prefix="/api/jobs",      tags=["Jobs"])
app.include_router(images.router,    prefix="/api/images",    tags=["Images"])
app.include_router(seo_audit.router, prefix="/api/seo-audit", tags=["Site Audit"])
app.include_router(google_ads.router, prefix="/api/google-ads", tags=["Google Ads"])
app.include_router(gbp.router,        prefix="/api/gbp",        tags=["Google Business Profile"])

from routes import indexing
app.include_router(indexing.router,  prefix="/api/indexing",  tags=["Google Indexing"])

from routes import seo_indexing
app.include_router(seo_indexing.router, prefix="/api/seo-indexing", tags=["Google Search Automation"])

# Instagram auto-posting
from routes import instagram
app.include_router(instagram.router, prefix="/api/instagram", tags=["Instagram"])

# 2026 AI-Tech routes
from routes import auth, streaming, semantic
app.include_router(auth.router,      prefix="/api/auth",      tags=["Authentication"])
app.include_router(streaming.router, prefix="/api/stream",    tags=["Streaming"])
app.include_router(semantic.router,  prefix="/api/semantic",  tags=["Semantic Search & AI"])

# ── Marketplace routes ──────────────────────────────────────────
from routes import marketplace_auth, marketplace
app.include_router(marketplace_auth.router, prefix="/api/users",       tags=["Users & Auth"])
app.include_router(marketplace.router,      prefix="/api/marketplace",  tags=["Marketplace"])


# ── Health & Observability ─────────────────────────────────────
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "2.1.0",
        "environment": settings.ENVIRONMENT
    }


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    try:
        from prometheus_client import generate_latest
        return generate_latest()
    except Exception as e:
        logger.error(f"Metrics generation failed: {e}")
        return {"error": "Metrics unavailable"}


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "status": "ok",
        "message": "SEO Automation API v2.1 running",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/robots.txt", response_class=PlainTextResponse, tags=["Public Pages"])
async def robots_txt(request: Request):
    """Permissive robots.txt for this app's own /p/{slug} pages, pointing
    crawlers at the sitemap. (The real WordPress site has its own, generated
    by its SEO plugin — this only covers pages hosted on this domain.)"""
    base = str(request.base_url).rstrip("/")
    return f"User-agent: *\nAllow: /\nSitemap: {base}/sitemap.xml\n"


@app.get("/sitemap.xml", tags=["Public Pages"])
async def sitemap_xml(request: Request, session=Depends(get_session)):
    """Standard XML sitemap listing every published /p/{slug} page on this
    app's own domain (WordPress posts have their own sitemap via RankMath/
    AIOSEO on the real site — this only covers this app's demo pages)."""
    from sqlalchemy import select
    from db import PageRecord
    from routes.pages import _public_base

    base = _public_base(request)
    rows = (await session.execute(select(PageRecord.slug, PageRecord.updated_at))).all()
    urls = "".join(
        f"<url><loc>{base}/p/{slug}</loc>"
        f"<lastmod>{updated_at.date().isoformat() if updated_at else ''}</lastmod></url>"
        for slug, updated_at in rows
    )
    xml = f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>'
    return Response(content=xml, media_type="application/xml")


# ── Public "Publish to Web" pages ───────────────────────────────
@app.get("/p/{slug}", response_class=HTMLResponse, tags=["Public Pages"])
async def public_page(slug: str, request: Request, session=Depends(get_session)):
    """Serve a published page as standalone, publicly viewable HTML."""
    from sqlalchemy import select
    from db import PageRecord
    from models.schemas import SEOBlock
    from services.public_page_service import render_public_html
    from routes.pages import _public_base

    result = await session.execute(select(PageRecord).where(PageRecord.slug == slug))
    row = result.scalar_one_or_none()
    if not row:
        return HTMLResponse(
            "<div style='font-family:sans-serif;text-align:center;padding:80px;color:#475569'>"
            "<h1 style='color:#0F172A'>404 — Page not found</h1>"
            "<p>This page hasn't been published yet.</p></div>",
            status_code=404,
        )
    block = SEOBlock(**row.seo_block)
    public_url = f"{_public_base(request)}/p/{slug}"
    return HTMLResponse(render_public_html(block, public_url))
