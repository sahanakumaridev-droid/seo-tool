"""
advanced_ai_service.py — Multi-model AI integration
Supports OpenAI (GPT-4), Anthropic (Claude), and Cohere
Includes streaming, caching, and fallback strategies
"""
import asyncio
import logging
from typing import Optional, AsyncGenerator, Dict, Any

import httpx
from bs4 import BeautifulSoup

from config import settings
from services.llm_service import chat_json

logger = logging.getLogger(__name__)

_MAX_PAGE_EXCERPT = 3000


async def _fetch_page_excerpt(url: str) -> str:
    """Best-effort fetch of a competitor's homepage text, so the analysis is
    grounded in real content instead of the LLM guessing from the URL alone.
    Returns '' on any failure — callers should degrade gracefully."""
    target = url if url.startswith(("http://", "https://")) else f"https://{url}"
    try:
        async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
            resp = await client.get(target)
        if resp.status_code != 200:
            return ""
        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer"]):
            tag.decompose()
        text = soup.get_text(" ", strip=True)
        return text[:_MAX_PAGE_EXCERPT]
    except Exception as e:
        logger.warning(f"Competitor page fetch failed for {url}: {e}")
        return ""


class AdvancedAIService:
    """Multi-model AI service with streaming and fallback."""
    
    def __init__(self):
        self.openai_enabled = bool(settings.OPENAI_API_KEY)
        self.anthropic_enabled = bool(settings.ANTHROPIC_API_KEY)
        self.cohere_enabled = bool(settings.COHERE_API_KEY)
        
        if self.openai_enabled:
            from openai import AsyncOpenAI
            self.openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        
        if self.anthropic_enabled:
            from anthropic import AsyncAnthropic
            self.anthropic_client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
        
        if self.cohere_enabled:
            import cohere
            self.cohere_client = cohere.AsyncClientV2(api_key=settings.COHERE_API_KEY)
    
    async def generate_content_with_streaming(
        self,
        prompt: str,
        model: str = "gpt-4",
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> AsyncGenerator[str, None]:
        """Generate content with streaming response."""
        
        if model.startswith("gpt"):
            async for chunk in self._stream_openai(prompt, model, temperature, max_tokens):
                yield chunk
        elif model.startswith("claude"):
            async for chunk in self._stream_anthropic(prompt, model, temperature, max_tokens):
                yield chunk
        elif model.startswith("command"):
            async for chunk in self._stream_cohere(prompt, model, temperature, max_tokens):
                yield chunk
        else:
            logger.error(f"Unknown model: {model}")
            yield "Error: Unknown model"
    
    async def _stream_openai(
        self,
        prompt: str,
        model: str,
        temperature: float,
        max_tokens: int
    ) -> AsyncGenerator[str, None]:
        """Stream from OpenAI."""
        if not self.openai_enabled:
            logger.warning("OpenAI not enabled")
            return
        
        try:
            stream = await self.openai_client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            logger.error(f"OpenAI streaming failed: {e}")
            yield f"Error: {str(e)}"
    
    async def _stream_anthropic(
        self,
        prompt: str,
        model: str,
        temperature: float,
        max_tokens: int
    ) -> AsyncGenerator[str, None]:
        """Stream from Anthropic Claude."""
        if not self.anthropic_enabled:
            logger.warning("Anthropic not enabled")
            return
        
        try:
            with self.anthropic_client.messages.stream(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}]
            ) as stream:
                for text in stream.text_stream:
                    yield text
        except Exception as e:
            logger.error(f"Anthropic streaming failed: {e}")
            yield f"Error: {str(e)}"
    
    async def _stream_cohere(
        self,
        prompt: str,
        model: str,
        temperature: float,
        max_tokens: int
    ) -> AsyncGenerator[str, None]:
        """Stream from Cohere."""
        if not self.cohere_enabled:
            logger.warning("Cohere not enabled")
            return
        
        try:
            stream = await self.cohere_client.chat(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True
            )
            
            async for event in stream:
                if hasattr(event, 'text'):
                    yield event.text
        except Exception as e:
            logger.error(f"Cohere streaming failed: {e}")
            yield f"Error: {str(e)}"
    
    async def analyze_competitor_strategy(
        self,
        competitor_url: str,
        business_type: str,
        city: str
    ) -> Dict[str, Any]:
        """AI-powered competitor analysis, grounded in the competitor's
        actual homepage content (not just a guess from the URL text)."""
        excerpt = await _fetch_page_excerpt(competitor_url)
        page_context = (
            f"Here is the actual visible text from their homepage:\n\"\"\"\n{excerpt}\n\"\"\"\n"
            if excerpt else
            "(Their homepage could not be fetched — base this on the URL and business context alone, "
            "and note in your analysis that the page content wasn't accessible.)\n"
        )
        prompt = f"""
        Analyze the competitor at {competitor_url} for a {business_type} business in {city}.
        {page_context}
        Provide:
        1. Key messaging and value propositions
        2. Target audience analysis
        3. SEO strategy (keywords, structure)
        4. Content strategy and gaps
        5. Unique selling points
        6. Recommendations for differentiation

        Respond as a JSON object with keys: messaging, target_audience, seo_strategy, content_gaps, unique_selling_points, recommendations.
        """

        data = await chat_json(prompt, temperature=0.6, max_tokens=2000)
        if not data:
            return {"error": "AI analysis unavailable — no LLM provider configured or the request failed."}
        return data

    async def discover_competitors(
        self,
        website: str,
        business_type: str,
        city: str
    ) -> Dict[str, Any]:
        """AI-powered competitor discovery, grounded in the user's own homepage
        content, so suggestions are relevant to what the business actually
        offers rather than a generic guess from business_type alone."""
        excerpt = await _fetch_page_excerpt(website)
        page_context = (
            f"Here is the actual visible text from their homepage:\n\"\"\"\n{excerpt}\n\"\"\"\n"
            if excerpt else
            "(Their homepage could not be fetched — base this on the business type and location alone.)\n"
        )
        prompt = f"""
        A {business_type} business in {city} has the website {website}.
        {page_context}
        Suggest 5 real, likely competitor businesses/websites that compete with them for
        local search visibility (same business type, same or nearby city). For each, give
        your best guess at their domain and a one-sentence rationale for why they're a
        likely competitor. Do not suggest {website} itself.

        Respond as a JSON object: {{"competitors": [{{"domain": "...", "rationale": "..."}}]}}
        """

        data = await chat_json(prompt, temperature=0.6, max_tokens=1200)
        if not data or not data.get("competitors"):
            return {"error": "AI competitor discovery unavailable — no LLM provider configured or the request failed.", "competitors": []}
        return data

    async def generate_seo_recommendations(
        self,
        current_content: str,
        target_keywords: list,
        business_type: str
    ) -> Dict[str, Any]:
        """Generate AI-powered SEO recommendations."""
        prompt = f"""
        Analyze this SEO content and provide recommendations:
        
        Current Content:
        {current_content}
        
        Target Keywords: {', '.join(target_keywords)}
        Business Type: {business_type}
        
        Provide:
        1. Keyword optimization suggestions
        2. Content structure improvements
        3. Meta tag recommendations
        4. Internal linking opportunities
        5. Schema markup suggestions
        6. Readability improvements
        
        Format as JSON with specific, actionable recommendations.
        """
        
        try:
            response = ""
            async for chunk in self.generate_content_with_streaming(
                prompt,
                model="gpt-4",
                max_tokens=2000
            ):
                response += chunk
            
            import json
            return json.loads(response)
        except Exception as e:
            logger.error(f"SEO recommendations failed: {e}")
            return {"error": str(e)}
    
    async def generate_content_variants(
        self,
        base_content: str,
        num_variants: int = 3,
        tone: str = "professional"
    ) -> list:
        """Generate multiple content variants with different tones."""
        prompt = f"""
        Generate {num_variants} variants of this content with a {tone} tone:
        
        {base_content}
        
        Each variant should:
        - Maintain the same core message
        - Use different phrasing and structure
        - Appeal to different audience segments
        - Vary in length and detail level
        
        Return as JSON array of variants.
        """
        
        try:
            response = ""
            async for chunk in self.generate_content_with_streaming(
                prompt,
                model="gpt-4",
                max_tokens=3000
            ):
                response += chunk
            
            import json
            return json.loads(response)
        except Exception as e:
            logger.error(f"Content variant generation failed: {e}")
            return []


# Singleton instance
advanced_ai_service = AdvancedAIService()


async def get_advanced_ai_service() -> AdvancedAIService:
    """Dependency injection for advanced AI service."""
    return advanced_ai_service
