"""News collector agent"""
import requests
from typing import Dict, Any, List
from rapidfuzz import fuzz
from langdetect import detect
from tenacity import retry, stop_after_attempt, wait_exponential

from .base import BaseAgent, Thought, Action
from ..memory.base import MemoryStore, MemoryEntry, MemoryType
from ..config import settings
import logging

logger = logging.getLogger(__name__)


class CollectorAgent(BaseAgent):
    """Agent responsible for collecting news titles"""
    
    def __init__(self, memory_store: MemoryStore):
        super().__init__("CollectorAgent", memory_store)
        self.api_key = settings.newsapi_key
        self.categories = settings.categories
        self.self_model["strengths"] = ["title_collection", "deduplication"]
    
    def _generate_thought(self, context: Dict[str, Any], 
                         memories: List[MemoryEntry]) -> Thought:
        """Generate thought about collection strategy"""
        category = context.get("category", "unknown")
        
        # Check past performance for this category
        relevant_memories = [m for m in memories 
                           if m.content.get("category") == category]
        
        reasoning = [
            f"Collecting from category: {category}",
            f"Found {len(relevant_memories)} relevant past experiences"
        ]
        
        confidence = 0.8
        if relevant_memories:
            avg_success = sum(1 for m in relevant_memories 
                            if m.content.get("success", False)) / len(relevant_memories)
            confidence = 0.5 + (avg_success * 0.5)
            reasoning.append(f"Historical success rate: {avg_success:.2%}")
        
        return Thought(
            content=f"Will collect titles from {category} with {settings.pages_per_category} pages",
            confidence=confidence,
            reasoning=reasoning,
            metadata={"category": category}
        )
    
    def _plan_action(self, thought: Thought) -> Action:
        """Plan collection action"""
        category = thought.metadata.get("category", "general")
        
        return Action(
            name="collect_titles",
            parameters={
                "category": category,
                "pages": settings.pages_per_category,
                "page_size": settings.page_size
            },
            expected_outcome=f"Collect ~{settings.page_size * settings.pages_per_category} titles",
            confidence=thought.confidence
        )
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    def _execute_action(self, action: Action) -> Dict[str, Any]:
        """Execute title collection"""
        category = action.parameters["category"]
        pages = action.parameters["pages"]
        page_size = action.parameters["page_size"]
        
        titles = []
        
        for page in range(1, pages + 1):
            try:
                url = (
                    f"https://newsapi.org/v2/top-headlines?"
                    f"category={category}&"
                    f"pageSize={page_size}&page={page}&"
                    f"language=en&"
                    f"apiKey={self.api_key}"
                )
                
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                data = response.json()
                
                if data.get("status") != "ok":
                    logger.warning(f"API error for {category}: {data.get('message')}")
                    break
                
                articles = data.get("articles", [])
                if not articles:
                    break
                
                for article in articles:
                    title = article.get("title")
                    source_name = article.get("source", {}).get("name", "")
                    
                    if title:
                        cleaned = self._clean_title(title, source_name)
                        if self._is_english(cleaned):
                            titles.append(cleaned)
                
            except Exception as e:
                logger.error(f"Error fetching page {page} for {category}: {e}")
                break
        
        # Deduplicate
        unique_titles = self._deduplicate(titles)
        
        result = {
            "success": len(unique_titles) > 0,
            "category": category,
            "raw_count": len(titles),
            "unique_count": len(unique_titles),
            "titles": unique_titles
        }
        
        # Learn from this experience
        self.learn({
            "action": "collect_titles",
            "category": category,
            "success": result["success"],
            "efficiency": len(unique_titles) / max(1, len(titles))
        })
        
        return result
    
    def _clean_title(self, title: str, source_name: str) -> str:
        """Clean title by removing source suffix"""
        if source_name and title.endswith(f" - {source_name}"):
            return title[:-(len(source_name) + 3)].strip()
        return title.strip()
    
    def _is_english(self, text: str) -> bool:
        """Check if text is English"""
        try:
            return detect(text) == 'en'
        except:
            return False
    
    def _deduplicate(self, titles: List[str]) -> List[str]:
        """Deduplicate similar titles"""
        unique = []
        for title in titles:
            if not any(fuzz.token_sort_ratio(title, existing) >= settings.similarity_threshold 
                      for existing in unique):
                unique.append(title)
        return unique
    
    def collect_all_categories(self) -> Dict[str, List[str]]:
        """Collect titles from all categories"""
        all_results = {}
        
        for category in self.categories:
            # Think about the task
            thought = self.think({"category": category})
            
            # Execute collection
            result = self.act(thought)
            
            if result["success"]:
                all_results[category] = result["titles"]
                logger.info(f"Collected {result['unique_count']} titles from {category}")
            
            # Periodic reflection
            if len(self.actions_taken) % settings.reflection_interval == 0:
                self.reflect("periodic")
        
        return all_results
