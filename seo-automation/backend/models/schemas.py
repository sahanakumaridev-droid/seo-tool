from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class GenerateRequest(BaseModel):
    business_type: str = Field(..., example="Plumbing")
    base_location: str = Field(..., example="San Diego, CA")
    num_cities: int = Field(default=10, ge=1, le=100)
    target_keywords: List[str] = Field(default=[], example=["emergency plumber san diego"])

class KeywordSet(BaseModel):
    primary: str
    secondary: List[str]
    long_tail: List[str]
    near_me: List[str]

class FAQItem(BaseModel):
    question: str
    answer: str

class SEOBlock(BaseModel):
    city: str
    state: str
    business_type: str
    title: str
    meta_description: str
    h1: str
    h2s: List[str]
    h3s: List[str]
    content: str
    faqs: List[FAQItem]
    cta: str
    keywords: KeywordSet
    schema_markup: Dict[str, Any]
    readability_score: Optional[float] = None
    keyword_density: Optional[float] = None

class SEOPage(BaseModel):
    id: Optional[str] = None
    business_type: str
    base_location: str
    city: str
    state: str
    slug: str
    seo_block: SEOBlock
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class BulkGenerateResponse(BaseModel):
    total: int
    pages: List[SEOBlock]
    job_id: str

class CityInfo(BaseModel):
    name: str
    state: str
    country: str
    latitude: float
    longitude: float
    population: Optional[int] = None
