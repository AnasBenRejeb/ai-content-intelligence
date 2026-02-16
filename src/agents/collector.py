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
        
        print(f"\n🔧 _execute_action called for category={category}, pages={pages}, page_size={page_size}")
        print(f"🔑 API Key present: {bool(self.api_key)}, length: {len(self.api_key) if self.api_key else 0}")
        
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
                
                print(f"📡 Fetching page {page}/{pages} for {category}...")
                
                response = requests.get(url, timeout=10)
                
                print(f"📥 Response status: {response.status_code}")
                
                response.raise_for_status()
                data = response.json()
                
                print(f"📊 API response status: {data.get('status')}")
                
                if data.get("status") != "ok":
                    print(f"❌ API error for {category}: {data.get('message')}")
                    logger.warning(f"API error for {category}: {data.get('message')}")
                    break
                
                articles = data.get("articles", [])
                print(f"📰 Received {len(articles)} articles from API")
                
                if not articles:
                    print(f"⚠️  No articles in response for page {page}")
                    break
                
                for article in articles:
                    title = article.get("title")
                    description = article.get("description", "")
                    content = article.get("content", "")
                    url = article.get("url", "")
                    source_name = article.get("source", {}).get("name", "")
                    published_at = article.get("publishedAt", "")
                    
                    if title:
                        cleaned_title = self._clean_title(title, source_name)
                        if self._is_english(cleaned_title):
                            # Store full article data, not just title
                            titles.append({
                                "title": cleaned_title,
                                "description": description,
                                "content": content,
                                "url": url,
                                "source": source_name,
                                "published_at": published_at
                            })
                
                print(f"✅ Processed {len(titles)} articles so far")
                
            except Exception as e:
                print(f"❌ Error fetching page {page} for {category}: {e}")
                logger.error(f"Error fetching page {page} for {category}: {e}")
                break
        
        print(f"📊 Total raw articles collected: {len(titles)}")
        
        # Deduplicate
        print("🔄 Deduplicating articles...")
        unique_articles = self._deduplicate(titles)
        print(f"✅ After deduplication: {len(unique_articles)} unique articles")
        
        result = {
            "success": len(unique_articles) > 0,
            "category": category,
            "raw_count": len(titles),
            "unique_count": len(unique_articles),
            "articles": unique_articles  # Changed from "titles" to "articles"
        }
        
        # Learn from this experience
        self.learn({
            "action": "collect_titles",
            "category": category,
            "success": result["success"],
            "efficiency": len(unique_articles) / max(1, len(titles))
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
    
    def _deduplicate(self, articles: List[Dict]) -> List[Dict]:
        """Deduplicate similar articles based on titles"""
        unique = []
        for article in articles:
            title = article["title"]
            if not any(fuzz.token_sort_ratio(title, existing["title"]) >= settings.similarity_threshold 
                      for existing in unique):
                unique.append(article)
        return unique
    
    def collect_all_categories(self) -> Dict[str, List[Dict]]:
        """Collect articles from all categories"""
        print(f"\n🔧 CollectorAgent.collect_all_categories() called")
        print(f"📋 Categories to process: {self.categories}")
        
        all_results = {}
        
        for category in self.categories:
            print(f"\n📰 Processing category: {category}")
            
            # Think about the task
            thought = self.think({"category": category})
            
            # Execute collection
            print(f"🔄 Executing collection for {category}...")
            result = self.act(thought)
            print(f"✅ Collection result: success={result['success']}, articles={result.get('unique_count', 0)}")
            
            if result["success"]:
                all_results[category] = result["articles"]  # Changed from "titles"
                logger.info(f"Collected {result['unique_count']} articles from {category}")
                print(f"✅ Stored {result['unique_count']} articles for {category}")
            else:
                print(f"❌ Collection failed for {category}")
            
            # Periodic reflection
            if len(self.actions_taken) % settings.reflection_interval == 0:
                self.reflect("periodic")
        
        print(f"\n🏁 collect_all_categories completed: {len(all_results)} categories, {sum(len(v) for v in all_results.values())} total articles")
        return all_results
