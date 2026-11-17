"""
llm_service.py
Provider-agnostic LLM helper so content generation can use FREE APIs.

Provider selection (config.LLM_PROVIDER, default "auto"):
  auto   -> groq, gemini, ollama, openai, anthropic
  groq   -> Groq (free tier, OpenAI-compatible endpoint)
  gemini -> Google Gemini (free tier, REST)
  ollama -> local free model (no API key)
  openai -> OpenAI (paid)
  anthropic -> Claude

All functions degrade gracefully: if no provider is configured they return None.
"""
import json
import re
from typing import Optional

import httpx
from config import settings


def _cloud_keys_ready() -> bool:
    """True when a free/paid cloud LLM key is configured (prefer over local Ollama)."""
    return bool(
        (settings.GROQ_API_KEY or "").strip()
        or (settings.GEMINI_API_KEY or "").strip()
        or (settings.ANTHROPIC_API_KEY or "").strip()
        or (settings.OPENAI_API_KEY or "").strip()
    )


def _ollama_on() -> bool:
    # When Groq/Gemini/etc. keys exist, skip local Ollama — it is slow and often
    # surfaces as "Writing with local AI" while cloud would finish in seconds.
    if _cloud_keys_ready():
        return False
    return bool(getattr(settings, "OLLAMA_ENABLED", True) and (settings.OLLAMA_BASE_URL or "").strip())


def active_provider() -> Optional[str]:
    """Return the provider we'll actually use, or None if none configured."""
    pref = (settings.LLM_PROVIDER or "auto").lower()
    aliases = {"chatgpt": "openai", "gpt": "openai", "gpt-4": "openai", "claude": "anthropic"}
    pref = aliases.get(pref, pref)
    have = {
        "groq": bool(settings.GROQ_API_KEY),
        "gemini": bool(settings.GEMINI_API_KEY),
        "ollama": _ollama_on(),
        "openai": bool(settings.OPENAI_API_KEY),
        "anthropic": bool(settings.ANTHROPIC_API_KEY),
    }
    # Fast free cloud first: Groq → Gemini → Claude → OpenAI → Ollama (only if no cloud keys).
    if pref in have and have[pref]:
        return pref
    for p in ("groq", "gemini", "anthropic", "openai", "ollama"):
        if have[p]:
            return p
    return None


def fast_provider_order(preferred: Optional[str] = None) -> list:
    """Ordered list of providers for generation — free cloud only by default.

    Skip OpenAI in auto mode: empty credits cause long 429 loops and make jobs look stuck.
    """
    aliases = {"chatgpt": "openai", "gpt": "openai", "gpt-4": "openai", "claude": "anthropic", "auto": ""}
    pref = aliases.get((preferred or "").lower().strip(), (preferred or "").lower().strip())
    have = {
        "groq": bool(settings.GROQ_API_KEY),
        "gemini": bool(settings.GEMINI_API_KEY),
        "anthropic": bool(settings.ANTHROPIC_API_KEY),
        "openai": bool(settings.OPENAI_API_KEY),
        "ollama": _ollama_on(),
    }
    order = []
    if pref and have.get(pref):
        order.append(pref)
    # Free + fast first. Do not auto-fall into OpenAI (paid / empty balance).
    for p in ("groq", "gemini", "anthropic"):
        if have.get(p) and p not in order:
            order.append(p)
    # Only use OpenAI when explicitly selected.
    if pref == "openai" and have.get("openai") and "openai" not in order:
        order.append("openai")
    if have.get("ollama") and "ollama" not in order:
        order.append("ollama")
    return order


def available_providers() -> dict:
    """Which providers have API keys configured (for the UI dropdown)."""
    claude = bool(settings.ANTHROPIC_API_KEY)
    return {
        "groq": bool(settings.GROQ_API_KEY),
        "gemini": bool(settings.GEMINI_API_KEY),
        "openai": bool(settings.OPENAI_API_KEY),
        "anthropic": claude,
        "claude": claude,
        "ollama": _ollama_on(),
        "active": active_provider(),
    }


def llm_available() -> bool:
    return active_provider() is not None


_OLLAMA_MODEL_CACHE: Optional[str] = None


async def _resolve_ollama_model() -> str:
    """Prefer a usable local model. Skip 0.5b toys when anything larger is installed."""
    global _OLLAMA_MODEL_CACHE
    if _OLLAMA_MODEL_CACHE:
        return _OLLAMA_MODEL_CACHE
    wanted = (settings.OLLAMA_MODEL or "").strip()
    root = (settings.OLLAMA_BASE_URL or "http://127.0.0.1:11434/v1").replace("/v1", "").rstrip("/")
    models = []
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            resp = await client.get(f"{root}/api/tags")
            if resp.status_code == 200:
                models = (resp.json() or {}).get("models") or []
    except Exception as e:
        print(f"[LLM] Ollama tags: {e}")

    def _score(m: dict) -> tuple:
        name = (m.get("name") or "").lower()
        size = int(m.get("size") or 0)
        tiny = 1 if (":0.5b" in name or "0.5b" in name) else 0
        return (tiny, -size, name)

    names = [(m or {}).get("name") or "" for m in models]
    names = [n for n in names if n]
    ranked = sorted(models, key=_score)
    usable = [m.get("name") for m in ranked if m.get("name") and ":0.5b" not in (m.get("name") or "").lower()]
    pick = ""
    if wanted and wanted in names and ":0.5b" not in wanted.lower():
        pick = wanted
    elif usable:
        pick = usable[0]
        if wanted and wanted != pick:
            print(f"[LLM] Skipping {wanted!r}; using {pick}")
    elif names:
        pick = names[0]
    _OLLAMA_MODEL_CACHE = pick or wanted or "llama3.2:latest"
    return _OLLAMA_MODEL_CACHE


def _extract_json(text: str) -> Optional[dict]:
    """Best-effort JSON extraction from a model response."""
    if not text:
        return None
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.IGNORECASE | re.MULTILINE)
    try:
        return json.loads(text)
    except Exception:
        pass
    m = re.search(r"\{.*\}", text, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(0))
        except Exception:
            try:
                obj, _ = json.JSONDecoder().raw_decode(m.group(0))
                return obj
            except Exception:
                pass
    # Local models often cut off mid-JSON; recover the main SEO fields.
    def _grab(key: str) -> str:
        mm = re.search(rf'"{re.escape(key)}"\s*:\s*"((?:\\.|[^"\\])*)"', text)
        if not mm:
            return ""
        return mm.group(1).replace('\\n', '\n').replace('\\"', '"')
    title = _grab("title")
    meta = _grab("meta_description")
    intro = _grab("intro")
    content = _grab("content")
    h1 = _grab("h1")
    if title and (intro or content or meta):
        return {
            "title": title,
            "meta_description": meta or intro[:160],
            "h1": h1 or title,
            "h2s": ["Getting started", "What to watch for", "When to get help"],
            "h3s": [],
            "intro": intro,
            "content": content or intro,
            "faqs": [],
            "cta": _grab("cta"),
        }
    return None


async def _ollama_fast(prompt: str, temperature: float, max_tokens: int, json_mode: bool) -> Optional[str]:
    """Native Ollama generate — small ctx so a page finishes in under a minute on CPU."""
    root = (settings.OLLAMA_BASE_URL or "http://127.0.0.1:11434/v1").replace("/v1", "").rstrip("/")
    model = await _resolve_ollama_model()
    # Keep enough of the keyword / industry brief; 1800 chars was truncating
    # PRIMARY KEYWORD + WHO lines and producing off-topic bodies.
    clipped = (prompt or "")[:4200]
    if json_mode:
        clipped = clipped + "\nJSON only."
    payload = {
        "model": model,
        "prompt": clipped,
        "stream": False,
        "keep_alive": "30m",
        "options": {
            "temperature": float(temperature or 0.7),
            "num_predict": min(max(int(max_tokens or 400), 200), 1100),
            "num_ctx": 4096,
        },
    }
    if json_mode:
        payload["format"] = "json"
    try:
        async with httpx.AsyncClient(timeout=25.0) as client:
            resp = await client.post(f"{root}/api/generate", json=payload)
            if resp.status_code != 200:
                print(f"[LLM] Ollama {resp.status_code}: {resp.text[:200]}")
                return None
            return (resp.json() or {}).get("response")
    except Exception as e:
        print(f"[LLM] Ollama error: {e}")
        return None


async def _openai_compatible(prompt: str, api_key: str, base_url: str, model: str,
                             temperature: float, max_tokens: int, json_mode: bool) -> Optional[str]:
    """Works for OpenAI, Groq, and Ollama (OpenAI-compatible API)."""
    try:
        from openai import AsyncOpenAI
        timeout = 20.0 if "11434" in (base_url or "") else 40.0
        client = AsyncOpenAI(
            api_key=api_key or "ollama",
            base_url=base_url,
            timeout=timeout,
            max_retries=0,
        ) if base_url else AsyncOpenAI(api_key=api_key, timeout=timeout, max_retries=0)
        kwargs = dict(model=model, messages=[{"role": "user", "content": prompt}],
                      temperature=temperature, max_tokens=max_tokens)
        local = "11434" in (base_url or "") or "ollama" in (base_url or "").lower()
        if json_mode and not local:
            kwargs["response_format"] = {"type": "json_object"}
        elif local:
            kwargs["messages"] = [
                {"role": "system", "content": "Return valid JSON only. No markdown fences."},
                {"role": "user", "content": prompt},
            ]
        resp = await client.chat.completions.create(**kwargs)
        return resp.choices[0].message.content
    except Exception as e:
        print(f"[LLM] OpenAI-compatible ({base_url or 'openai'}) error: {e}")
        return None


async def _gemini(prompt: str, temperature: float, max_tokens: int, json_mode: bool) -> Optional[str]:
    model = settings.GEMINI_MODEL
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    gen_cfg = {"temperature": temperature, "maxOutputTokens": max_tokens}
    if json_mode:
        gen_cfg["responseMimeType"] = "application/json"
    payload = {"contents": [{"parts": [{"text": prompt}]}], "generationConfig": gen_cfg}
    try:
        async with httpx.AsyncClient(timeout=40) as client:
            resp = await client.post(url, params={"key": settings.GEMINI_API_KEY}, json=payload)
            if resp.status_code != 200:
                print(f"[LLM] Gemini {resp.status_code}: {resp.text[:200]}")
                return None
            data = resp.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        print(f"[LLM] Gemini error: {e}")
        return None


async def _anthropic(prompt: str, temperature: float, max_tokens: int) -> Optional[str]:
    if not settings.ANTHROPIC_API_KEY:
        return None
    try:
        async with httpx.AsyncClient(timeout=22) as client:
            resp = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": settings.ANTHROPIC_API_KEY,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": settings.ANTHROPIC_MODEL or "claude-3-haiku-20240307",
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                    "messages": [{"role": "user", "content": prompt}],
                },
            )
            if resp.status_code != 200:
                print(f"[LLM] Anthropic {resp.status_code}: {resp.text[:200]}")
                return None
            data = resp.json()
            parts = data.get("content") or []
            return "".join(p.get("text", "") for p in parts if p.get("type") == "text") or None
    except Exception as e:
        print(f"[LLM] Anthropic error: {e}")
        return None


def _provider_have() -> dict:
    return {
        "groq": bool(settings.GROQ_API_KEY),
        "gemini": bool(settings.GEMINI_API_KEY),
        "ollama": _ollama_on(),
        "openai": bool(settings.OPENAI_API_KEY),
        "anthropic": bool(settings.ANTHROPIC_API_KEY),
    }


async def _call_provider(provider: str, prompt: str, temperature: float, max_tokens: int, json_mode: bool) -> Optional[str]:
    if provider == "groq":
        return await _openai_compatible(prompt, settings.GROQ_API_KEY,
                                        "https://api.groq.com/openai/v1", settings.GROQ_MODEL,
                                        temperature, max_tokens, json_mode=json_mode)
    if provider == "gemini":
        return await _gemini(prompt, temperature, max_tokens, json_mode=json_mode)
    if provider == "ollama":
        return await _ollama_fast(prompt, temperature, max_tokens, json_mode=json_mode)
    if provider == "openai":
        return await _openai_compatible(prompt, settings.OPENAI_API_KEY, "", "gpt-4o-mini",
                                        temperature, max_tokens, json_mode=json_mode)
    if provider == "anthropic":
        extra = "\n\nRespond with valid JSON only, no markdown fences." if json_mode else ""
        return await _anthropic(prompt + extra, temperature, max_tokens)
    return None


async def chat_text(prompt: str, temperature: float = 0.7, max_tokens: int = 3500,
                     provider: Optional[str] = None) -> Optional[str]:
    aliases = {"chatgpt": "openai", "gpt": "openai", "gpt-4": "openai", "claude": "anthropic"}
    provider = aliases.get((provider or "").lower(), provider) if provider else None
    provider = provider or active_provider()
    return await _call_provider(provider, prompt, temperature, max_tokens, json_mode=False)


async def chat_json(prompt: str, temperature: float = 0.7, max_tokens: int = 3500,
                     provider: Optional[str] = None, timeout: float = 40) -> Optional[dict]:
    """One fast provider, then a single backup. Do not walk every key (each miss waits on timeout)."""
    import asyncio
    order = fast_provider_order(provider)[:2]
    for prov in order:
        try:
            raw = await asyncio.wait_for(
                _call_provider(prov, prompt, temperature, max_tokens, json_mode=True),
                timeout=timeout,
            )
        except asyncio.TimeoutError:
            print(f"[LLM] {prov} timed out")
            raw = None
        parsed = _extract_json(raw) if raw else None
        if parsed:
            return parsed
    return None
