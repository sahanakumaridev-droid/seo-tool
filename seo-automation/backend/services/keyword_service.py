import httpx
from typing import List
from models.schemas import KeywordSet

async def fetch_datamuse_words(query: str, max_results: int = 10) -> List[str]:
    """Fetch related words from Datamuse API (free, no key needed)."""
    try:
        async with httpx.AsyncClient(timeout=8) as client:
            resp = await client.get(
                "https://api.datamuse.com/words",
                params={"ml": query, "max": max_results}
            )
            data = resp.json()
            return [item["word"] for item in data if "word" in item]
    except Exception:
        return []

def _build_user_questions(bt: str, city: str, state: str) -> List[str]:
    """Real user questions sourced from PAA / Google Suggest patterns."""
    bt_l = bt.lower()
    return [
        f"How much does {bt_l} cost in {city}?",
        f"Who is the best {bt_l} in {city}?",
        f"What does a {bt_l} do in {city}?",
        f"How do I find a reliable {bt_l} in {city}, {state}?",
        f"Is {bt_l} worth it for small businesses in {city}?",
        f"What should I look for when hiring a {bt_l} in {city}?",
        f"How long does {bt_l} take in {city}?",
        f"Do I need a {bt_l} for my business in {city}?",
    ]

async def generate_keywords(business_type: str, city: str, state: str) -> KeywordSet:
    city_lower = city.lower()
    bt = business_type.lower()

    primary = f"{bt} {city_lower}"

    # Fetch related terms from Datamuse
    related = await fetch_datamuse_words(f"{bt} services", max_results=8)

    # Short-tail / main keywords
    secondary = [
        f"{bt}",
        f"website {bt}",
        f"business {bt}",
        f"best {bt} in {city_lower}",
        f"affordable {bt} {city_lower}",
        f"professional {bt} {city_lower}",
        f"local {bt} company {city_lower}",
        f"{bt} contractor {city_lower}",
    ]
    if related:
        secondary += [f"{w} {city_lower}" for w in related[:3]]

    # Long-tail keywords
    long_tail = [
        f"best {bt} services in {city}, {state}",
        f"affordable {bt} company near {city}",
        f"top rated {bt} {city_lower} {state}",
        f"licensed {bt} in {city_lower}",
        f"small business {bt} in {city_lower}",
        f"professional {bt} for contractors in {city_lower}",
        f"cheap {bt} services {city_lower}",
        f"custom {bt} {city_lower}",
        f"{bt} agency {city_lower}",
        f"hire {bt} expert {city_lower}",
    ]

    near_me = [
        f"{bt} near me",
        f"{bt} services near me",
        f"best {bt} near me",
        f"{bt} company near me",
        f"local {bt} near me",
    ]

    user_questions = _build_user_questions(business_type, city, state)

    return KeywordSet(
        primary=primary,
        secondary=secondary[:10],
        long_tail=long_tail,
        near_me=near_me,
        user_questions=user_questions,
    )
