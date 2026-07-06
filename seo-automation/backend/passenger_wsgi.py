"""
passenger_wsgi.py — entry point for cPanel/Namecheap "Setup Python App" (Passenger).

Passenger serves WSGI apps, but FastAPI is ASGI, so we wrap it with a2wsgi.
cPanel looks for a module-level `application` callable in this file.
For local dev keep using: uvicorn main:app --reload
"""
from a2wsgi import ASGIMiddleware
from main import app as _asgi_app

application = ASGIMiddleware(_asgi_app)
