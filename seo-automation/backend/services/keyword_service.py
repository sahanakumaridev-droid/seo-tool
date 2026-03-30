import httpx
from typing import List
from models.schemas import KeywordSet

async def fetch_datamuse_words(query: str, rel_type: str = None, max_results: int = 10) -> List[str]:
    """Fetch related words from Datamuse API (free, no key needed)."""
    params = {"ml": query, "max": max_results}
    if rel_type:
        params[rel_type] = query
        del params["ml"]
    try:
        async with httpx.AsyncClient(timeout=8) as client:
            resp = await client.get("https://api.datamuse.com/words", params=params)
            data = resp.json()
            return [item["word"] for item in data if "word" in item]
    except Exception:
        return []

async def generate_keywords(business_type: str, city: str, state: str) -> KeywordSet:
    location = f"{city}, {state}"
    bt = business_type.lower()
    city_lower = city.lower()

    primary = f"{bt} services {city_lower}"

    # Fetch related terms from Datamuse
    related = await fetch_datamuse_words(f"{bt} services", max_results=8)

    secondary = [
        f"best {bt} in {city_lower}",
        f"affordable {bt} {city_lower}",
        f"professional {bt} {city_lower}",
        f"local {bt} company {city_lower}",
        f"{bt} contractor {city_lower}",
    ]
    if related:
        secondary += [f"{w} {city_lower}" for w in related[:3]]

    long_tail = [
        f"best {bt} services in {city}, {state}",
        f"affordable {bt} company near {city}",
        f"emergency {bt} services {city_lower}",
        f"licensed {bt} contractor in {city_lower}",
        f"top rated {bt} {city_lower} {state}",
        f"24 hour {bt} services {city_lower}",
        f"residential {bt} services {city_lower}",
        f"commercial {bt} services {city_lower}",
    ]

    near_me = [
        f"{bt} near me",
        f"{bt} services near me",
        f"best {bt} near me",
        f"{bt} company near me",
        f"local {bt} near me",
    ]

    return KeywordSet(
        primary=primary,
        secondary=secondary[:8],
        long_tail=long_tail,
        near_me=near_me
    )
