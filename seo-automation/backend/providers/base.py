"""Provider abstractions for external SEO data sources.

Each provider is an ABC with a single async entrypoint. The mock
implementations in this package return deterministic, plausibly-shaped
data so the frontend can be built against a stable contract; swapping in
a real integration (PageSpeed Insights, a SERP/keyword-data vendor, etc.)
later means writing a new class that satisfies the same interface —
no caller-side changes required.
"""
from abc import ABC, abstractmethod

from models.schemas import AuditResult, KeywordResearchResult


class SiteAuditProvider(ABC):
    @abstractmethod
    async def run_audit(self, url: str) -> AuditResult:
        ...


class KeywordDataProvider(ABC):
    @abstractmethod
    async def research(self, keyword: str, location: str = "US") -> KeywordResearchResult:
        ...
