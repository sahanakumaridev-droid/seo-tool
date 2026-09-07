import asyncio
from services.rag_service import (
    chunk_text,
    format_context,
    retrieve,
    site_key,
    _INDEX,
)


def test_chunk_text_splits_long_copy():
    text = "word " * 400
    parts = chunk_text(text, size=80, overlap=10)
    assert len(parts) > 1
    assert all(parts)


def test_site_key_strips_www():
    assert site_key("https://www.ZeOrbit.com/blog") == "zeorbit.com"


def test_retrieve_token_overlap():
    _INDEX["acme.test"] = [
        {
            "url": "https://acme.test/hvac",
            "title": "HVAC",
            "text": "We install heat pumps and air conditioning in Austin.",
            "embedding": [],
        },
        {
            "url": "https://acme.test/legal",
            "title": "Legal",
            "text": "Our attorneys handle contracts only.",
            "embedding": [],
        },
    ]

    async def _run():
        hits = await retrieve("heat pump air conditioning Austin", "https://acme.test")
        assert hits
        assert "hvac" in hits[0]["url"]
        block = format_context(hits)
        assert "RETRIEVED SITE CONTEXT" in block
        assert "heat pumps" in block.lower()

    asyncio.run(_run())
    _INDEX.pop("acme.test", None)
