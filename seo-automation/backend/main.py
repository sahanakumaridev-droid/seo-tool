import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse, PlainTextResponse, Response, RedirectResponse
from fastapi.staticfiles import StaticFiles
from db import get_session
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from routes import locations, content, pages, keywords, wordpress
from routes import social, leads, jobs, images, seo_audit, google_ads, gbp
try:
    from routes import google_live
except ImportError:  # older deploys may lack this module
    google_live = None
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
        origin for origin in [
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://127.0.0.1:5175",
            "http://127.0.0.1:5180",
            "https://zeorbit.com",
            "https://www.zeorbit.com",
            os.getenv("FRONTEND_URL", ""),
        ] if origin
    ],
    allow_origin_regex=r"https://([a-z0-9-]+\.)?zeorbit\.com",
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
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
from routes import google_reviews
app.include_router(google_reviews.router, prefix="/api/google-reviews", tags=["Google Reviews"])
if google_live is not None:
    app.include_router(google_live.router, prefix="/api/google",     tags=["Google Live Automation"])

from routes import indexing
app.include_router(indexing.router,  prefix="/api/indexing",  tags=["Google Indexing"])

from routes import seo_indexing
app.include_router(seo_indexing.router, prefix="/api/seo-indexing", tags=["Google Search Automation"])

from routes import rankings
app.include_router(rankings.router, prefix="/api/rankings", tags=["Rankings"])

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
@app.api_route("/health", methods=["GET", "HEAD"])
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


@app.api_route("/robots.txt", methods=["GET", "HEAD"], response_class=PlainTextResponse, tags=["Public Pages"])
async def robots_txt(request: Request):
    """Allow search + LLM crawlers; point them at page/post sitemaps and llms.txt."""
    from routes.pages import _public_base
    base = _public_base(request).rstrip("/")
    return (
        "User-agent: *\n"
        "Allow: /\n"
        "Allow: /llms.txt\n"
        "Allow: /.well-known/llms.txt\n"
        "\n"
        "User-agent: Googlebot\nAllow: /\n"
        "User-agent: Google-Extended\nAllow: /\nAllow: /llms.txt\n"
        "User-agent: Google-CloudVertexBot\nAllow: /\nAllow: /llms.txt\n"
        "User-agent: Google-InspectionTool\nAllow: /\n"
        "User-agent: bingbot\nAllow: /\n"
        "User-agent: Applebot\nAllow: /\n"
        "User-agent: Applebot-Extended\nAllow: /\nAllow: /llms.txt\n"
        "User-agent: GPTBot\nAllow: /\nAllow: /llms.txt\n"
        "User-agent: ChatGPT-User\nAllow: /\nAllow: /llms.txt\n"
        "User-agent: OAI-SearchBot\nAllow: /\n"
        "User-agent: ClaudeBot\nAllow: /\nAllow: /llms.txt\n"
        "User-agent: Claude-User\nAllow: /\n"
        "User-agent: Claude-SearchBot\nAllow: /\n"
        "User-agent: PerplexityBot\nAllow: /\nAllow: /llms.txt\n"
        "User-agent: Amazonbot\nAllow: /\n"
        "User-agent: DuckDuckBot\nAllow: /\n"
        "User-agent: Bytespider\nAllow: /\n"
        "User-agent: CCBot\nAllow: /\n"
        "User-agent: meta-externalagent\nAllow: /\n"
        f"\nSitemap: {base}/sitemap.xml\n"
        f"Sitemap: {base}/page-sitemap.xml\n"
        f"Sitemap: {base}/post-sitemap.xml\n"
    )


@app.get("/google{token}.html", response_class=PlainTextResponse, tags=["Public Pages"])
async def google_site_verification_file(token: str):
    """Serve Search Console HTML-file verification when configured."""
    fname = (settings.GSC_VERIFICATION_FILENAME or "").strip()
    body = (settings.GSC_VERIFICATION_FILE_BODY or "").strip()
    expected = f"google{token}.html"
    if not fname or not body or fname != expected:
        return PlainTextResponse("Not found", status_code=404)
    return PlainTextResponse(body, media_type="text/html")


def _content_kind_of(block) -> str:
    if isinstance(block, dict):
        ct = (block.get("content_type") or "service").lower()
    else:
        ct = "service"
    return "post" if ct in ("blog", "post") else "page"


# Real ZeOrbit marketing routes that must always appear in page-sitemap.xml
# (Google must discover these even when no SEO tool pages are published yet).
_SITE_MENU_PATHS = (
    "/",
    "/website-designing",
    "/mobile-apps",
    "/seo-ppc",
    "/custom-software",
    "/portfolio",
    "/contact",
    "/blog",
)


async def _sitemap_urlset(request, session, kind: str | None):
    from routes.pages import _public_base
    from datetime import date

    base = _public_base(request).rstrip("/")
    parts = []
    today = date.today().isoformat()

    # Page sitemap = live marketing menu ONLY.
    # Do NOT auto-list SEO-tool drafts / location test pages — those duplicate
    # thin URLs and pollute Google's crawl of zeorbit.com.
    if kind in (None, "page"):
        for path in _SITE_MENU_PATHS:
            loc = base if path == "/" else f"{base}{path}"
            parts.append(
                f"<url><loc>{loc}</loc><lastmod>{today}</lastmod>"
                f"<changefreq>weekly</changefreq><priority>1.0</priority></url>"
            )

    # Post sitemap stays empty of tool-generated test blogs.
    # Real editorial posts live on the marketing site (/blog) and are not
    # mirrored as SEO-tool PageRecords (that caused duplicate content).
    if kind in (None, "post"):
        pass

    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        + "".join(parts)
        + "</urlset>"
    )
    return Response(
        content=xml,
        media_type="application/xml",
        headers={
            "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
            "Pragma": "no-cache",
        },
    )


@app.api_route("/sitemap.xml", methods=["GET", "HEAD"], tags=["Public Pages"])
async def sitemap_xml(request: Request, session=Depends(get_session)):
    """Sitemap index pointing at page vs post sitemaps."""
    from routes.pages import _public_base
    base = _public_base(request)
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        f"<sitemap><loc>{base}/page-sitemap.xml</loc></sitemap>"
        f"<sitemap><loc>{base}/post-sitemap.xml</loc></sitemap>"
        "</sitemapindex>"
    )
    return Response(
        content=xml,
        media_type="application/xml",
        headers={
            "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
            "Pragma": "no-cache",
        },
    )


@app.api_route("/page-sitemap.xml", methods=["GET", "HEAD"], tags=["Public Pages"])
async def page_sitemap_xml(request: Request, session=Depends(get_session)):
    return await _sitemap_urlset(request, session, "page")


@app.api_route("/post-sitemap.xml", methods=["GET", "HEAD"], tags=["Public Pages"])
async def post_sitemap_xml(request: Request, session=Depends(get_session)):
    return await _sitemap_urlset(request, session, "post")


# ── Public published articles at /{slug} (never /p/ in the address bar) ──
_RESERVED_ARTICLE_SLUGS = {
    "docs", "redoc", "openapi.json", "health", "metrics", "static",
    "robots.txt", "sitemap.xml", "page-sitemap.xml", "post-sitemap.xml", "favicon.ico", "api",
}


async def _render_public_article(slug: str, request: Request, session):
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
    public_url = f"{_public_base(request)}/{slug}"
    return HTMLResponse(render_public_html(block, public_url))


@app.api_route("/p/{slug}", methods=["GET", "HEAD"], tags=["Public Pages"])
async def public_page_legacy(slug: str, request: Request):
    """Old /p/{slug} links 301 to /{slug} so /p/ never stays in the URL."""
    from routes.pages import _public_base
    return RedirectResponse(url=f"{_public_base(request)}/{slug}", status_code=301)


@app.api_route("/{slug}", methods=["GET", "HEAD"], response_class=HTMLResponse, tags=["Public Pages"])
async def public_page(slug: str, request: Request, session=Depends(get_session)):
    """Serve a published page at https://zeorbit.com/{keyword}-{city}."""
    if slug in _RESERVED_ARTICLE_SLUGS or "." in slug:
        return HTMLResponse("Not found", status_code=404)
    return await _render_public_article(slug, request, session)
