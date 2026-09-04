"""
llm_service.py
Provider-agnostic LLM helper so content generation can use FREE APIs.

Provider selection (config.LLM_PROVIDER, default "auto"):
  auto   -> first available of: groq, gemini, openai
  groq   -> Groq (free tier, OpenAI-compatible endpoint)
  gemini -> Google Gemini (free tier, REST)
  openai -> OpenAI (paid)

All functions degrade gracefully: if no provider is configured they return None,
and callers fall back to the template engine.
"""
import json
import re
from typing import Optional

import httpx
from config import settings


def active_provider() -> Optional[str]:
    """Return the provider we'll actually use, or None if none configured."""
    pref = (settings.LLM_PROVIDER or "auto").lower()
    # Normalize aliases from the UI
    aliases = {"chatgpt": "openai", "gpt": "openai", "gpt-4": "openai", "claude": "anthropic"}
    pref = aliases.get(pref, pref)
    have = {
        "groq": bool(settings.GROQ_API_KEY),
        "gemini": bool(settings.GEMINI_API_KEY),
        "openai": bool(settings.OPENAI_API_KEY),
        "anthropic": bool(settings.ANTHROPIC_API_KEY),
    }
    if pref in have:
        return pref if have[pref] else None
    for p in ("gemini", "groq", "openai", "anthropic"):  # Gemini first for query-relevant copy
        if have[p]:
            return p
    return None


def available_providers() -> dict:
    """Which providers have API keys configured (for the UI dropdown)."""
    return {
        "groq": bool(settings.GROQ_API_KEY),
        "gemini": bool(settings.GEMINI_API_KEY),
        "openai": bool(settings.OPENAI_API_KEY),
        "anthropic": bool(settings.ANTHROPIC_API_KEY),
        "active": active_provider(),
    }


def llm_available() -> bool:
    return active_provider() is not None


def _extract_json(text: str) -> Optional[dict]:
    """Best-effort JSON extraction from a model response."""
    if not text:
        return None
    text = text.strip()
    # Strip markdown fences if present.
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
            return None
    return None


async def _openai_compatible(prompt: str, api_key: str, base_url: str, model: str,
                             temperature: float, max_tokens: int, json_mode: bool) -> Optional[str]:
    """Works for both OpenAI and Groq (OpenAI-compatible API)."""
    try:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=api_key, base_url=base_url) if base_url else AsyncOpenAI(api_key=api_key)
        kwargs = dict(model=model, messages=[{"role": "user", "content": prompt}],
                      temperature=temperature, max_tokens=max_tokens)
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}
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
        async with httpx.AsyncClient(timeout=60) as client:
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
        async with httpx.AsyncClient(timeout=90) as client:
            resp = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": settings.ANTHROPIC_API_KEY,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": "claude-3-5-sonnet-20241022",
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


async def chat_text(prompt: str, temperature: float = 0.7, max_tokens: int = 3500,
                     provider: Optional[str] = None) -> Optional[str]:
    """Return raw text from the active provider, or None. Pass `provider` to
    override the global setting for just this call (e.g. a per-request
    user choice), without mutating global state."""
    aliases = {"chatgpt": "openai", "gpt": "openai", "gpt-4": "openai", "claude": "anthropic"}
    provider = aliases.get((provider or "").lower(), provider) if provider else None
    provider = provider or active_provider()
    if provider == "groq":
        return await _openai_compatible(prompt, settings.GROQ_API_KEY,
                                        "https://api.groq.com/openai/v1", settings.GROQ_MODEL,
                                        temperature, max_tokens, json_mode=False)
    if provider == "gemini":
        return await _gemini(prompt, temperature, max_tokens, json_mode=False)
    if provider == "openai":
        return await _openai_compatible(prompt, settings.OPENAI_API_KEY, "", "gpt-4o",
                                        temperature, max_tokens, json_mode=False)
    if provider == "anthropic":
        return await _anthropic(prompt, temperature, max_tokens)
    return None


async def chat_json(prompt: str, temperature: float = 0.7, max_tokens: int = 3500,
                     provider: Optional[str] = None) -> Optional[dict]:
    """Return a parsed JSON object from the active provider, or None. Pass
    `provider` to override the global setting for just this call."""
    aliases = {"chatgpt": "openai", "gpt": "openai", "gpt-4": "openai", "claude": "anthropic"}
    provider = aliases.get((provider or "").lower(), provider) if provider else None
    provider = provider or active_provider()
    raw = None
    if provider == "groq":
        raw = await _openai_compatible(prompt, settings.GROQ_API_KEY,
                                       "https://api.groq.com/openai/v1", settings.GROQ_MODEL,
                                       temperature, max_tokens, json_mode=True)
    elif provider == "gemini":
        raw = await _gemini(prompt, temperature, max_tokens, json_mode=True)
    elif provider == "openai":
        raw = await _openai_compatible(prompt, settings.OPENAI_API_KEY, "", "gpt-4o",
                                       temperature, max_tokens, json_mode=True)
    elif provider == "anthropic":
        raw = await _anthropic(
            prompt + "\n\nRespond with valid JSON only, no markdown fences.",
            temperature, max_tokens,
        )
    return _extract_json(raw) if raw else None
