"""Article retriever agent"""
import requests
from typing import Dict, Any, List, Optional
from pathlib import Path
import re
from tenacity import retry, stop_after_attempt, wait_exponential

from .base import BaseAgent, Thought, Action
from ..memory.base import MemoryStore, MemoryEntry, MemoryType
from ..config import settings
import logging

logger = logging.getLogger(__name__)


class RetrieverAgent(BaseAgent):
    """Agent responsible for retrieving full article content"""
    
    def __init__(self, memory_store: MemoryStore):
        super().__init__("RetrieverAgent", memory_store)
        self.gnews_api_key = settings.gnews_api_key
        self.articles_dir = settings.articles_dir
        self.articles_dir.mkdir(parents=True, exist_ok=True)
        self.self_model["strengths"] = ["article_retrieval", "content_extraction"]
    
    def _generate_thought(self, context: Dict[str, Any], 
                         memories: List[MemoryEntry]) -> Thought:
        """Generate thought about retrieval strategy"""
        query = context.get("query", "")
        title = context.get("title", "")
        
        reasoning = [
            f"Searching for article: {title[:40]}...",
            f"Using query: {query}"
        ]
        
        # Check cache
        cached = self._check_cache(title)
        if cached:
            reasoning.append("Found in cache")
            confidence = 0.95
        else:
            reasoning.append("Not in cache, will fetch from API")
            confidence = 0.7
        
        return Thought(
            content=f"Retrieve article for: {title[:30]}...",
            confidence=confidence,
            reasoning=reasoning,
            metadata={"query": query, "title": title, "cached": cached}
        )
    
    def _plan_action(self, thought: Thought) -> Action:
        """Plan retrieval action"""
        return Action(
            name="retrieve_article",
            parameters={
                "query": thought.metadata["query"],
                "title": thought.metadata["title"],
                "use_cache": thought.metadata["cached"]
            },
            expected_outcome="Retrieve full article text",
            confidence=thought.confidence
        )
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    def _execute_action(self, action: Action) -> Dict[str, Any]:
        """Execute article retrieval"""
        title = action.parameters["title"]
        query = action.parameters["query"]
        
        # Check cache first
        if action.parameters["use_cache"]:
            cached_path = self._get_cache_path(title)
            if cached_path.exists():
                with open(cached_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                return {
                    "success": True,
                    "title": title,
                    "content": content,
                    "source": "cache",
                    "path": str(cached_path)
                }
        
        # Fetch from API
        try:
            url = self._search_gnews(query)
            if url:
                content = self._fetch_article_content(url)
                if content:
                    # Save to cache
                    saved_path = self._save_article(title, content)
                    
                    result = {
                        "success": True,
                        "title": title,
                        "content": content,
                        "source": "api",
                        "url": url,  # Include URL for duplicate detection
                        "path": str(saved_path)
                    }
                    
                    # Learn from success
                    self.learn({
                        "action": "retrieve_article",
                        "success": True,
                        "source": "api"
                    })
                    
                    return result
        
        except Exception as e:
            logger.error(f"Error retrieving article: {e}")
        
        return {
            "success": False,
            "title": title,
            "error": "Failed to retrieve article"
        }
    
    def _search_gnews(self, query: str) -> Optional[str]:
        """Search GNews for article URL"""
        try:
            params = {
                "q": query,
                "lang": "en",
                "token": self.gnews_api_key,
                "max": 1
            }
            
            response = requests.get(
                "https://gnews.io/api/v4/search",
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("totalArticles", 0) > 0:
                    return data["articles"][0].get("url")
        
        except Exception as e:
            logger.warning(f"GNews search failed: {e}")
        
        return None
    
    def _fetch_article_content(self, url: str) -> Optional[str]:
        """Fetch article content from URL"""
        try:
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            # Simple content extraction - can be enhanced with BeautifulSoup
            return response.text[:5000]  # Limit content size
        except Exception as e:
            logger.warning(f"Failed to fetch content from {url}: {e}")
            return None
    
    def _save_article(self, title: str, content: str) -> Path:
        """Save article to disk"""
        filename = self._sanitize_filename(title)
        filepath = self.articles_dir / f"{filename}.txt"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return filepath
    
    def _check_cache(self, title: str) -> bool:
        """Check if article is in cache"""
        return self._get_cache_path(title).exists()
    
    def _get_cache_path(self, title: str) -> Path:
        """Get cache path for title"""
        filename = self._sanitize_filename(title)
        return self.articles_dir / f"{filename}.txt"
    
    def _sanitize_filename(self, title: str) -> str:
        """Sanitize title for filename"""
        # Remove invalid characters
        filename = re.sub(r'[<>:"/\\|?*]', '', title)
        # Replace spaces with underscores
        filename = filename.replace(' ', '_')
        # Limit length
        return filename[:100]
    
    def retrieve_batch(self, analyses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Retrieve a batch of articles"""
        results = []
        
        for i, analysis in enumerate(analyses):
            if not analysis.get("success"):
                continue
            
            # Think about retrieval
            thought = self.think({
                "title": analysis["title"],
                "query": analysis["query"]
            })
            
            # Execute retrieval
            result = self.act(thought)
            results.append(result)
            
            # Periodic reflection
            if (i + 1) % settings.reflection_interval == 0:
                self.reflect("periodic")
        
        return results
