"""
semantic_service.py — Semantic search using embeddings
Integrates with Pinecone for vector similarity search
Enables AI-powered competitor analysis and content recommendations
"""
import asyncio
from typing import List, Dict, Any, Optional
from config import settings
import logging
import os

logger = logging.getLogger(__name__)

# Initialize embedding model (runs locally, no API calls)
# Handle cache permission errors gracefully
embedding_model = None
try:
    # Set cache directory to a writable location
    cache_dir = os.path.expanduser('~/.cache/huggingface')
    os.makedirs(cache_dir, exist_ok=True)
    
    from sentence_transformers import SentenceTransformer
    embedding_model = SentenceTransformer('all-MiniLM-L6-v2', cache_folder=cache_dir)
    logger.info("Semantic search model loaded successfully")
except Exception as e:
    logger.warning(f"Failed to load semantic search model: {e}. Semantic search will be disabled.")
    embedding_model = None


class SemanticSearchService:
    """Semantic search using embeddings and vector similarity."""
    
    def __init__(self):
        self.model = embedding_model
        self.enabled = embedding_model is not None
        self.pinecone_enabled = bool(settings.PINECONE_API_KEY) and self.enabled
        
        if not self.enabled:
            logger.warning("Semantic search is disabled (model not loaded)")
        
        if self.pinecone_enabled:
            try:
                from pinecone import Pinecone
                self.pc = Pinecone(api_key=settings.PINECONE_API_KEY)
                self.index = self.pc.Index(settings.PINECONE_INDEX_NAME)
            except Exception as e:
                logger.warning(f"Pinecone initialization failed: {e}")
                self.pinecone_enabled = False
    
    async def embed_text(self, text: str) -> List[float]:
        """Generate embedding for text."""
        if not self.enabled:
            logger.warning("Semantic search disabled, returning empty embedding")
            return []
        
        loop = asyncio.get_event_loop()
        embedding = await loop.run_in_executor(
            None, 
            lambda: self.model.encode(text, convert_to_tensor=False)
        )
        return embedding.tolist()
    
    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts."""
        if not self.enabled:
            logger.warning("Semantic search disabled, returning empty embeddings")
            return [[] for _ in texts]
        
        loop = asyncio.get_event_loop()
        embeddings = await loop.run_in_executor(
            None,
            lambda: self.model.encode(texts, convert_to_tensor=False)
        )
        return embeddings.tolist()
    
    async def find_similar_content(
        self, 
        query: str, 
        business_type: str,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """Find similar content using semantic search."""
        if not self.pinecone_enabled:
            logger.warning("Pinecone not enabled, returning empty results")
            return []
        
        try:
            query_embedding = await self.embed_text(query)
            
            # Search Pinecone
            results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                filter={"business_type": business_type},
                include_metadata=True
            )
            
            return [
                {
                    "id": match.id,
                    "score": match.score,
                    "metadata": match.metadata
                }
                for match in results.matches
            ]
        except Exception as e:
            logger.error(f"Semantic search failed: {e}")
            return []
    
    async def store_content_embedding(
        self,
        content_id: str,
        content: str,
        business_type: str,
        city: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Store content embedding in Pinecone."""
        if not self.pinecone_enabled:
            return False
        
        try:
            embedding = await self.embed_text(content)
            
            meta = {
                "business_type": business_type,
                "city": city,
                **(metadata or {})
            }
            
            self.index.upsert(
                vectors=[(content_id, embedding, meta)]
            )
            return True
        except Exception as e:
            logger.error(f"Failed to store embedding: {e}")
            return False
    
    async def analyze_competitor_content(
        self,
        competitor_content: str,
        business_type: str,
        city: str
    ) -> Dict[str, Any]:
        """Analyze competitor content and find gaps."""
        try:
            # Get embedding for competitor content
            competitor_embedding = await self.embed_text(competitor_content)
            
            # Find similar content in our database
            similar = await self.find_similar_content(
                competitor_content,
                business_type,
                top_k=10
            )
            
            # Analyze gaps
            gaps = {
                "content_similarity": similar,
                "unique_angles": await self._extract_unique_angles(
                    competitor_content,
                    business_type
                ),
                "keyword_opportunities": await self._find_keyword_gaps(
                    competitor_content,
                    business_type,
                    city
                )
            }
            
            return gaps
        except Exception as e:
            logger.error(f"Competitor analysis failed: {e}")
            return {}
    
    async def _extract_unique_angles(
        self,
        content: str,
        business_type: str
    ) -> List[str]:
        """Extract unique angles from content."""
        # This would integrate with Claude/GPT-4 for analysis
        # For now, return placeholder
        return [
            "Local expertise angle",
            "Affordability focus",
            "Speed of delivery",
            "Customer testimonials",
            "Warranty/guarantee"
        ]
    
    async def _find_keyword_gaps(
        self,
        content: str,
        business_type: str,
        city: str
    ) -> List[Dict[str, Any]]:
        """Find keyword opportunities based on competitor content."""
        # This would integrate with keyword research APIs
        # For now, return placeholder
        return [
            {"keyword": f"best {business_type} in {city}", "difficulty": "medium"},
            {"keyword": f"affordable {business_type}", "difficulty": "high"},
            {"keyword": f"{business_type} near me", "difficulty": "high"},
        ]


# Singleton instance
semantic_service = SemanticSearchService()


async def get_semantic_service() -> SemanticSearchService:
    """Dependency injection for semantic service."""
    return semantic_service
