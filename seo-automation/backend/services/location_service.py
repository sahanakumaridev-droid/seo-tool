import httpx
import math
from typing import List
from models.schemas import CityInfo
from config import settings

# Hardcoded San Diego area cities as reliable fallback (Phase 1)
SD_NEARBY_CITIES = [
    {"name": "La Jolla", "state": "CA", "lat": 32.8328, "lon": -117.2713, "pop": 46781},
    {"name": "Chula Vista", "state": "CA", "lat": 32.6401, "lon": -117.0842, "pop": 275487},
    {"name": "El Cajon", "state": "CA", "lat": 32.7948, "lon": -116.9625, "pop": 103614},
    {"name": "Escondido", "state": "CA", "lat": 33.1192, "lon": -117.0864, "pop": 151038},
    {"name": "Oceanside", "state": "CA", "lat": 33.1959, "lon": -117.3795, "pop": 174068},
    {"name": "Carlsbad", "state": "CA", "lat": 33.1581, "lon": -117.3506, "pop": 114746},
    {"name": "Vista", "state": "CA", "lat": 33.2000, "lon": -117.2425, "pop": 101838},
    {"name": "San Marcos", "state": "CA", "lat": 33.1434, "lon": -117.1661, "pop": 96664},
    {"name": "Santee", "state": "CA", "lat": 32.8384, "lon": -116.9739, "pop": 58610},
    {"name": "Poway", "state": "CA", "lat": 32.9628, "lon": -117.0359, "pop": 50008},
    {"name": "La Mesa", "state": "CA", "lat": 32.7678, "lon": -117.0228, "pop": 60304},
    {"name": "Spring Valley", "state": "CA", "lat": 32.7448, "lon": -116.9989, "pop": 31230},
    {"name": "Lemon Grove", "state": "CA", "lat": 32.7248, "lon": -117.0314, "pop": 27984},
    {"name": "National City", "state": "CA", "lat": 32.6781, "lon": -117.0992, "pop": 61776},
    {"name": "Coronado", "state": "CA", "lat": 32.6859, "lon": -117.1831, "pop": 24697},
    {"name": "Imperial Beach", "state": "CA", "lat": 32.5839, "lon": -117.1131, "pop": 27183},
    {"name": "Encinitas", "state": "CA", "lat": 33.0369, "lon": -117.2920, "pop": 62444},
    {"name": "Del Mar", "state": "CA", "lat": 32.9595, "lon": -117.2653, "pop": 4161},
    {"name": "Solana Beach", "state": "CA", "lat": 32.9912, "lon": -117.2712, "pop": 13380},
    {"name": "Rancho Santa Fe", "state": "CA", "lat": 33.0228, "lon": -117.2003, "pop": 3117},
    {"name": "Lakeside", "state": "CA", "lat": 32.8576, "lon": -116.9225, "pop": 20648},
    {"name": "Alpine", "state": "CA", "lat": 32.8351, "lon": -116.7664, "pop": 14236},
    {"name": "Ramona", "state": "CA", "lat": 33.0417, "lon": -116.8731, "pop": 20292},
    {"name": "Fallbrook", "state": "CA", "lat": 33.3764, "lon": -117.2511, "pop": 30534},
    {"name": "Bonsall", "state": "CA", "lat": 33.2878, "lon": -117.2267, "pop": 4220},
    {"name": "Valley Center", "state": "CA", "lat": 33.2192, "lon": -117.0317, "pop": 10834},
    {"name": "Pauma Valley", "state": "CA", "lat": 33.3281, "lon": -116.9789, "pop": 1200},
    {"name": "Borrego Springs", "state": "CA", "lat": 33.2556, "lon": -116.3750, "pop": 3429},
    {"name": "Julian", "state": "CA", "lat": 33.0784, "lon": -116.6019, "pop": 1621},
    {"name": "Pine Valley", "state": "CA", "lat": 32.8248, "lon": -116.5289, "pop": 1500},
    {"name": "Jamul", "state": "CA", "lat": 32.7198, "lon": -116.8764, "pop": 6163},
    {"name": "Bonita", "state": "CA", "lat": 32.6623, "lon": -117.0281, "pop": 12538},
    {"name": "Otay Ranch", "state": "CA", "lat": 32.6200, "lon": -116.9800, "pop": 35000},
    {"name": "Mira Mesa", "state": "CA", "lat": 32.9137, "lon": -117.1431, "pop": 72000},
    {"name": "Scripps Ranch", "state": "CA", "lat": 32.9284, "lon": -117.0781, "pop": 30000},
    {"name": "Rancho Bernardo", "state": "CA", "lat": 33.0131, "lon": -117.0742, "pop": 48000},
    {"name": "Rancho Penasquitos", "state": "CA", "lat": 32.9631, "lon": -117.1214, "pop": 55000},
    {"name": "Carmel Valley", "state": "CA", "lat": 32.9431, "lon": -117.2114, "pop": 45000},
    {"name": "Tierrasanta", "state": "CA", "lat": 32.8431, "lon": -117.0814, "pop": 32000},
    {"name": "Mission Valley", "state": "CA", "lat": 32.7731, "lon": -117.1514, "pop": 38000},
    {"name": "North Park", "state": "CA", "lat": 32.7431, "lon": -117.1214, "pop": 42000},
    {"name": "Hillcrest", "state": "CA", "lat": 32.7531, "lon": -117.1614, "pop": 28000},
    {"name": "Ocean Beach", "state": "CA", "lat": 32.7431, "lon": -117.2514, "pop": 15000},
    {"name": "Pacific Beach", "state": "CA", "lat": 32.7931, "lon": -117.2414, "pop": 42000},
    {"name": "Mission Beach", "state": "CA", "lat": 32.7731, "lon": -117.2514, "pop": 5000},
    {"name": "Point Loma", "state": "CA", "lat": 32.7231, "lon": -117.2414, "pop": 35000},
    {"name": "Clairemont", "state": "CA", "lat": 32.8231, "lon": -117.1914, "pop": 65000},
    {"name": "Kearny Mesa", "state": "CA", "lat": 32.8331, "lon": -117.1514, "pop": 22000},
    {"name": "Serra Mesa", "state": "CA", "lat": 32.8031, "lon": -117.1314, "pop": 25000},
    {"name": "College Area", "state": "CA", "lat": 32.7731, "lon": -117.0714, "pop": 30000},
]

def haversine(lat1, lon1, lat2, lon2) -> float:
    R = 3958.8  # miles
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    return R * 2 * math.asin(math.sqrt(a))

async def get_nearby_cities(base_location: str, num_cities: int = 50) -> List[CityInfo]:
    """
    Phase 1: Returns cities from hardcoded SD list sorted by distance.
    Phase 2: Will use OpenCage + GeoDB APIs.
    """
    # Try OpenCage to geocode base location
    base_lat, base_lon = 32.7157, -117.1611  # San Diego default

    if settings.OPENCAGE_API_KEY:
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(
                    "https://api.opencagedata.com/geocode/v1/json",
                    params={"q": base_location, "key": settings.OPENCAGE_API_KEY, "limit": 1}
                )
                data = resp.json()
                if data.get("results"):
                    geo = data["results"][0]["geometry"]
                    base_lat, base_lon = geo["lat"], geo["lng"]
        except Exception:
            pass

    # Sort by distance from base
    cities_with_dist = []
    for c in SD_NEARBY_CITIES:
        dist = haversine(base_lat, base_lon, c["lat"], c["lon"])
        cities_with_dist.append((dist, c))

    cities_with_dist.sort(key=lambda x: x[0])

    result = []
    for _, c in cities_with_dist[:num_cities]:
        result.append(CityInfo(
            name=c["name"],
            state=c["state"],
            country="USA",
            latitude=c["lat"],
            longitude=c["lon"],
            population=c.get("pop")
        ))
    return result
