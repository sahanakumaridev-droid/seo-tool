"""
rag_service.py — Retrieve site chunks, then pass them into LLM prompts.

Uses local MiniLM embeddings (same model as semantic_service). Pinecone is optional
and not required. Degrades to token-overlap ranking if embeddings fail to load.
"""
from __future__ import annotations

import math
import re
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse

from services.semantic_service import semantic_service

_CHUNK_CHARS = 900
_CHUNK_OVERLAP = 120
_TOP_K = 5

# origin -> list of {url, title, text, embedding}
_INDEX: Dict[str, List[dict]] = {}


_ATTEMPTED: set = set()


def site_key(url: str) -> str:
    if not url:
        return ""
    parsed = urlparse(url if "://" in url else f"https://{url}")
    host = (parsed.netloc or "").lower().removeprefix("www.")
    return host


def already_tried(url: str) -> bool:
    key = site_key(url)
    return bool(key and key in _ATTEMPTED)


def mark_tried(url: str) -> None:
    key = site_key(url)
    if key:
        _ATTEMPTED.add(key)


def has_index(url: str) -> bool:
    key = site_key(url)
    return bool(key and _INDEX.get(key))


def chunk_text(text: str, size: int = _CHUNK_CHARS, overlap: int = _CHUNK_OVERLAP) -> List[str]:
    raw = re.sub(r"\s+", " ", (text or "")).strip()
    if not raw:
        return []
    if len(raw) <= size:
        return [raw]
    chunks = []
    i = 0
    while i < len(raw):
        chunks.append(raw[i : i + size])
        i += max(1, size - overlap)
    return chunks


def _cosine(a: List[float], b: List[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = 0.0
    na = 0.0
    nb = 0.0
    for x, y in zip(a, b):
        dot += x * y
        na += x * x
        nb += y * y
    if na <= 0 or nb <= 0:
        return 0.0
    return dot / (math.sqrt(na) * math.sqrt(nb))


def _token_score(query: str, text: str) -> float:
    q = {t for t in re.findall(r"[a-z0-9]{3,}", (query or "").lower())}
    if not q:
        return 0.0
    blob = (text or "").lower()
    hits = sum(1 for t in q if t in blob)
    return hits / len(q)


async def index_documents(site_url: str, documents: List[dict]) -> int:
    """Index {url, title, text} docs for a site. Replaces any prior index for that host."""
    key = site_key(site_url)
    if not key:
        return 0
    _ATTEMPTED.add(key)
    rows: List[dict] = []
    texts: List[str] = []
    meta: List[Tuple[str, str, str]] = []
    for doc in documents or []:
        url = (doc.get("url") or "").strip()
        title = (doc.get("title") or "")[:120]
        for part in chunk_text(doc.get("text") or ""):
            texts.append(part)
            meta.append((url, title, part))
    embeddings: List[List[float]] = []
    if texts and semantic_service.enabled:
        try:
            embeddings = await semantic_service.embed_batch(texts)
        except Exception as e:
            print(f"[RAG] embed_batch failed: {e}")
            embeddings = []
    for i, (url, title, part) in enumerate(meta):
        emb = embeddings[i] if i < len(embeddings) else []
        rows.append({"url": url, "title": title, "text": part, "embedding": emb})
    _INDEX[key] = rows
    print(f"[RAG] indexed {len(rows)} chunks for {key} from {len(documents or [])} pages")
    return len(rows)


async def retrieve(query: str, site_url: str, top_k: int = _TOP_K) -> List[dict]:
    key = site_key(site_url)
    rows = _INDEX.get(key) or []
    if not rows or not (query or "").strip():
        return []
    q_emb: List[float] = []
    if semantic_service.enabled and any(r.get("embedding") for r in rows):
        try:
            q_emb = await semantic_service.embed_text(query)
        except Exception as e:
            print(f"[RAG] query embed failed: {e}")
            q_emb = []
    scored = []
    for row in rows:
        if q_emb and row.get("embedding"):
            score = _cosine(q_emb, row["embedding"])
        else:
            score = _token_score(query, f"{row.get('title', '')} {row.get('text', '')}")
        scored.append((score, row))
    scored.sort(key=lambda x: x[0], reverse=True)
    seen_text = set()
    out = []
    for score, row in scored:
        if score <= 0:
            continue
        sig = (row.get("text") or "")[:80]
        if sig in seen_text:
            continue
        seen_text.add(sig)
        out.append({
            "url": row.get("url") or "",
            "title": row.get("title") or "",
            "text": row.get("text") or "",
            "score": round(float(score), 4),
        })
        if len(out) >= top_k:
            break
    return out


def format_context(chunks: List[dict], max_chars: int = 2800) -> str:
    if not chunks:
        return ""
    lines = [
        "RETRIEVED SITE CONTEXT (RAG — facts from the live website. Do not invent services, "
        "prices, or claims that are not supported here. If context is thin, stay general and honest.)"
    ]
    used = 0
    for i, c in enumerate(chunks, 1):
        piece = f"\n[{i}] {c.get('title') or c.get('url')}\nSource: {c.get('url')}\n{(c.get('text') or '')[:700]}"
        if used + len(piece) > max_chars:
            break
        lines.append(piece)
        used += len(piece)
    return "\n".join(lines)


async def rag_prompt_block(query: str, site_url: str) -> str:
    chunks = await retrieve(query, site_url)
    return format_context(chunks)


def preferred_urls(chunks: List[dict]) -> List[str]:
    urls = []
    seen = set()
    for c in chunks:
        u = (c.get("url") or "").strip()
        if u and u not in seen:
            seen.add(u)
            urls.append(u)
    return urls
