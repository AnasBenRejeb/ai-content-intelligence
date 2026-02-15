"""News analyzer agent with keyword extraction"""
from typing import Dict, Any, List
from keybert import KeyBERT

from .base import BaseAgent, Thought, Action
from ..memory.base import MemoryStore, MemoryEntry, MemoryType
from ..config import settings
import logging

logger = logging.getLogger(__name__)


class AnalyzerAgent(BaseAgent):
    """Agent responsible for analyzing titles and extracting keywords"""
    
    def __init__(self, memory_store: MemoryStore):
        super().__init__("AnalyzerAgent", memory_store)
        self.kw_model = KeyBERT()
        self.self_model["strengths"] = ["keyword_extraction", "semantic_analysis"]
    
    def _generate_thought(self, context: Dict[str, Any], 
                         memories: List[MemoryEntry]) -> Thought:
        """Generate thought about analysis strategy"""
        title = context.get("title", "")
        
        reasoning = [
            f"Analyzing title: {title[:50]}...",
            "Will extract top keywords for search optimization"
        ]
        
        # Check if we've seen similar titles
        similar_count = sum(1 for m in memories 
                          if m.type == MemoryType.SEMANTIC 
                          and any(word in m.content.get("title", "") 
                                for word in title.split()[:3]))
        
        if similar_count > 0:
            reasoning.append(f"Found {similar_count} similar past analyses")
        
        confidence = 0.75 + (min(similar_count, 5) * 0.05)
        
        return Thought(
            content=f"Extract keywords from: {title[:30]}...",
            confidence=confidence,
            reasoning=reasoning,
            metadata={"title": title}
        )
    
    def _plan_action(self, thought: Thought) -> Action:
        """Plan keyword extraction action"""
        return Action(
            name="extract_keywords",
            parameters={
                "title": thought.metadata["title"],
                "top_n": 5,
                "ngram_range": (1, 2)
            },
            expected_outcome="Extract 3-5 relevant keywords",
            confidence=thought.confidence
        )
    
    def _execute_action(self, action: Action) -> Dict[str, Any]:
        """Execute keyword extraction"""
        title = action.parameters["title"]
        
        try:
            # Extract keywords
            keywords = self.kw_model.extract_keywords(
                title,
                keyphrase_ngram_range=action.parameters["ngram_range"],
                stop_words='english',
                top_n=action.parameters["top_n"]
            )
            
            # Extract phrases and deduplicate words
            keyword_phrases = [kw[0] for kw in keywords]
            seen = set()
            deduplicated_words = []
            
            for phrase in keyword_phrases:
                for word in phrase.split():
                    if word.lower() not in seen:
                        seen.add(word.lower())
                        deduplicated_words.append(word)
            
            query = " ".join(deduplicated_words)
            
            result = {
                "success": len(deduplicated_words) > 0,
                "title": title,
                "keywords": keyword_phrases,
                "query": query,
                "word_count": len(deduplicated_words)
            }
            
            # Store in semantic memory
            memory_entry = MemoryEntry(
                id=f"analysis_{hash(title)}",
                type=MemoryType.SEMANTIC,
                content={
                    "title": title,
                    "keywords": keyword_phrases,
                    "query": query
                },
                timestamp=self.actions_taken[-1].timestamp if self.actions_taken else None,
                importance=0.6
            )
            self.memory.store(memory_entry)
            
            # Learn from this
            self.learn({
                "action": "extract_keywords",
                "success": result["success"],
                "keyword_count": len(keyword_phrases)
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Error extracting keywords: {e}")
            return {
                "success": False,
                "title": title,
                "error": str(e)
            }
    
    def analyze_batch(self, titles: List[str]) -> List[Dict[str, Any]]:
        """Analyze a batch of titles"""
        results = []
        
        for i, title in enumerate(titles):
            # Think about the analysis
            thought = self.think({"title": title})
            
            # Execute analysis
            result = self.act(thought)
            results.append(result)
            
            # Periodic reflection
            if (i + 1) % settings.reflection_interval == 0:
                self.reflect("periodic")
        
        return results
