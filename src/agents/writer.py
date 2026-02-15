"""Article writer agent using local LLM"""
from typing import Dict, Any, List, Optional
from pathlib import Path
import logging
from rapidfuzz import fuzz

from .base import BaseAgent, Thought, Action
from ..memory.base import MemoryStore, MemoryEntry, MemoryType
from ..config import settings

logger = logging.getLogger(__name__)


class WriterAgent(BaseAgent):
    """Agent responsible for generating articles using LLM"""
    
    def __init__(self, memory_store: MemoryStore, model_path: Optional[str] = None):
        super().__init__("WriterAgent", memory_store)
        self.model_path = model_path or settings.llm_model_path
        self.llm = None
        self.generated_dir = settings.generated_articles_dir
        self.generated_dir.mkdir(parents=True, exist_ok=True)
        self.self_model["strengths"] = ["article_generation", "content_synthesis"]
        
        # Initialize LLM
        self._init_llm()
    
    def _init_llm(self):
        """Initialize the LLM"""
        try:
            from llama_cpp import Llama
            
            if not Path(self.model_path).exists():
                logger.warning(f"LLM model not found at {self.model_path}")
                logger.info("WriterAgent will operate in mock mode")
                return
            
            logger.info(f"Loading LLM from {self.model_path}")
            self.llm = Llama(
                model_path=str(self.model_path),
                n_ctx=4096,
                n_threads=4,
                n_gpu_layers=0  # Set to >0 if you have GPU
            )
            logger.info("✅ LLM loaded successfully")
            
        except ImportError:
            logger.warning("llama-cpp-python not installed. Install with: pip install llama-cpp-python")
            logger.info("WriterAgent will operate in mock mode")
        except Exception as e:
            logger.error(f"Failed to load LLM: {e}")
            logger.info("WriterAgent will operate in mock mode")
    
    def _generate_thought(self, context: Dict[str, Any], 
                         memories: List[MemoryEntry]) -> Thought:
        """Generate thought about article generation"""
        title = context.get("title", "")
        source_content = context.get("content", "")
        source_url = context.get("url", "")
        
        reasoning = [
            f"Generating article for: {title[:40]}...",
            f"Source content length: {len(source_content)} chars"
        ]
        
        # Check if we've already generated from this source
        already_generated = self._check_if_already_generated(title, source_url, memories)
        
        if already_generated:
            reasoning.append("⚠️  Already generated article from this source!")
            reasoning.append("Will skip to avoid duplication")
            return Thought(
                content=f"Skip duplicate: {title[:30]}...",
                confidence=0.95,
                reasoning=reasoning,
                metadata={
                    "title": title,
                    "has_llm": self.llm is not None,
                    "skip_duplicate": True,
                    "previous_generation": already_generated
                }
            )
        
        # Check if we have the LLM
        if self.llm:
            reasoning.append("Using local LLM for generation")
            confidence = 0.85
        else:
            reasoning.append("Using template-based generation (LLM not available)")
            confidence = 0.6
        
        # Check for similar past generations
        similar_count = sum(1 for m in memories 
                          if m.type == MemoryType.SEMANTIC 
                          and "article_generation" in m.content.get("action", ""))
        
        if similar_count > 0:
            reasoning.append(f"Generated {similar_count} articles before (learning from patterns)")
            confidence += 0.05
        
        return Thought(
            content=f"Generate article: {title[:30]}...",
            confidence=min(confidence, 0.95),
            reasoning=reasoning,
            metadata={
                "title": title,
                "has_llm": self.llm is not None,
                "skip_duplicate": False,
                "source_url": source_url
            }
        )
    
    def _plan_action(self, thought: Thought) -> Action:
        """Plan article generation action"""
        if thought.metadata.get("skip_duplicate"):
            return Action(
                name="skip_duplicate",
                parameters={
                    "title": thought.metadata["title"],
                    "reason": "Already generated from this source"
                },
                expected_outcome="Skip duplicate generation",
                confidence=thought.confidence
            )
        
        return Action(
            name="generate_article",
            parameters={
                "title": thought.metadata["title"],
                "use_llm": thought.metadata["has_llm"],
                "source_url": thought.metadata.get("source_url", "")
            },
            expected_outcome="Generate unique article based on source",
            confidence=thought.confidence
        )
    
    def _execute_action(self, action: Action) -> Dict[str, Any]:
        """Execute article generation"""
        title = action.parameters["title"]
        
        # Handle duplicate skip
        if action.name == "skip_duplicate":
            logger.info(f"⏭️  Skipping duplicate: {title[:50]}...")
            return {
                "success": False,
                "title": title,
                "skipped": True,
                "reason": "Already generated from this source"
            }
        
        try:
            source_url = action.parameters.get("source_url", "")
            
            if action.parameters["use_llm"] and self.llm:
                article = self._generate_with_llm(title)
            else:
                article = self._generate_template(title)
            
            if article:
                # Save generated article with metadata
                saved_path = self._save_article(title, article)
                metadata = self._create_metadata(title, source_url, article)
                self._save_metadata(title, metadata)
                
                result = {
                    "success": True,
                    "title": title,
                    "article": article,
                    "word_count": len(article.split()),
                    "path": str(saved_path),
                    "method": "llm" if action.parameters["use_llm"] else "template",
                    "source_url": source_url,
                    "metadata": metadata
                }
                
                # Store in memory with metadata
                self._store_generation_memory(result)
                
                # Learn from success
                self.learn({
                    "action": "generate_article",
                    "success": True,
                    "method": result["method"],
                    "word_count": result["word_count"],
                    "title": title,
                    "source_url": source_url
                })
                
                return result
        
        except Exception as e:
            logger.error(f"Error generating article: {e}")
        
        return {
            "success": False,
            "title": title,
            "error": "Failed to generate article"
        }
    
    def _generate_with_llm(self, title: str, source_content: str = "") -> str:
        """Generate article using LLM"""
        prompt = self._create_prompt(title, source_content)
        
        try:
            response = self.llm(
                prompt,
                max_tokens=1000,
                temperature=0.7,
                top_p=0.9,
                stop=["</article>", "\n\n\n"]
            )
            
            article = response["choices"][0]["text"].strip()
            return article
            
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            return self._generate_template(title)
    
    def _create_prompt(self, title: str, source_content: str = "") -> str:
        """Create prompt for LLM"""
        if source_content:
            prompt = f"""<s>[INST] You are a professional journalist. Write a comprehensive, well-structured article based on the following information.

Title: {title}

Source Information:
{source_content[:1000]}

Write a complete article (300-500 words) that:
1. Has a compelling introduction
2. Provides detailed information
3. Maintains journalistic objectivity
4. Includes relevant context
5. Has a strong conclusion

Article: [/INST]

"""
        else:
            prompt = f"""<s>[INST] You are a professional journalist. Write a comprehensive article about the following topic.

Title: {title}

Write a complete article (300-500 words) that:
1. Has a compelling introduction
2. Provides detailed information
3. Maintains journalistic objectivity
4. Includes relevant context
5. Has a strong conclusion

Article: [/INST]

"""
        return prompt
    
    def _generate_template(self, title: str) -> str:
        """Generate article using template (fallback)"""
        article = f"""# {title}

## Introduction

This article explores the topic of "{title}", examining its key aspects and implications.

## Background

The subject has gained significant attention recently, with various stakeholders weighing in on its importance and potential impact.

## Key Points

Several important factors contribute to understanding this topic:

1. **Context**: The broader context surrounding this development
2. **Implications**: What this means for various stakeholders
3. **Future Outlook**: Potential developments and trends

## Analysis

Experts suggest that this topic represents an important development in its field. The various perspectives and considerations highlight the complexity of the issue.

## Conclusion

As this situation continues to evolve, it will be important to monitor developments and understand the broader implications for all involved parties.

---
*This article was generated by an AI system for informational purposes.*
"""
        return article
    
    def _save_article(self, title: str, content: str) -> Path:
        """Save generated article"""
        # Sanitize filename
        filename = self._sanitize_filename(title)
        filepath = self.generated_dir / f"{filename}.md"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return filepath
    
    def _sanitize_filename(self, title: str) -> str:
        """Sanitize title for filename"""
        import re
        filename = re.sub(r'[<>:"/\\|?*]', '', title)
        filename = filename.replace(' ', '_')
        return filename[:100]
    
    def _check_if_already_generated(self, title: str, source_url: str, 
                                    memories: List[MemoryEntry]) -> Optional[Dict]:
        """Check if we've already generated an article from this source"""
        # Check memory for previous generations
        for memory in memories:
            if memory.type == MemoryType.SEMANTIC:
                content = memory.content
                if content.get("action") == "generate_article":
                    # Check by title similarity
                    stored_title = content.get("title", "")
                    if self._titles_similar(title, stored_title):
                        return {
                            "title": stored_title,
                            "timestamp": memory.timestamp,
                            "source_url": content.get("source_url", "")
                        }
                    
                    # Check by source URL
                    if source_url and content.get("source_url") == source_url:
                        return {
                            "title": stored_title,
                            "timestamp": memory.timestamp,
                            "source_url": source_url
                        }
        
        # Also check if file already exists
        filename = self._sanitize_filename(title)
        filepath = self.generated_dir / f"{filename}.md"
        if filepath.exists():
            return {
                "title": title,
                "file_exists": True,
                "path": str(filepath)
            }
        
        return None
    
    def _titles_similar(self, title1: str, title2: str, threshold: int = 85) -> bool:
        """Check if two titles are similar using fuzzy matching"""
        return fuzz.token_sort_ratio(title1, title2) >= threshold
    
    def _create_metadata(self, title: str, source_url: str, article: str) -> Dict[str, Any]:
        """Create metadata for generated article"""
        import hashlib
        from datetime import datetime
        
        # Create content hash for duplicate detection
        content_hash = hashlib.md5(article.encode()).hexdigest()
        
        return {
            "title": title,
            "source_url": source_url,
            "generated_at": datetime.now().isoformat(),
            "word_count": len(article.split()),
            "content_hash": content_hash,
            "agent": "WriterAgent",
            "model": "mistral-7b" if self.llm else "template"
        }
    
    def _save_metadata(self, title: str, metadata: Dict[str, Any]):
        """Save metadata alongside article"""
        import json
        
        filename = self._sanitize_filename(title)
        metadata_path = self.generated_dir / f"{filename}_metadata.json"
        
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
    
    def _store_generation_memory(self, result: Dict[str, Any]):
        """Store generation in memory for future duplicate detection"""
        memory_entry = MemoryEntry(
            id=f"generation_{hash(result['title'])}_{result.get('source_url', '')}",
            type=MemoryType.SEMANTIC,
            content={
                "action": "generate_article",
                "title": result["title"],
                "source_url": result.get("source_url", ""),
                "word_count": result["word_count"],
                "method": result["method"],
                "content_hash": result["metadata"]["content_hash"]
            },
            timestamp=self.actions_taken[-1].timestamp if self.actions_taken else None,
            importance=0.8  # High importance for duplicate detection
        )
        self.memory.store(memory_entry)
    
    def generate_batch(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate a batch of articles with smart duplicate detection"""
        results = []
        skipped = 0
        
        for i, article_data in enumerate(articles):
            if not article_data.get("success"):
                continue
            
            # Think about generation (includes duplicate check)
            thought = self.think({
                "title": article_data.get("title", ""),
                "content": article_data.get("content", ""),
                "url": article_data.get("url", "")
            })
            
            # Execute generation (or skip if duplicate)
            result = self.act(thought)
            results.append(result)
            
            if result.get("skipped"):
                skipped += 1
                logger.info(f"⏭️  Skipped duplicate ({skipped} total)")
            else:
                logger.info(f"✅ Generated: {result.get('title', '')[:50]}...")
            
            # Periodic reflection
            if (i + 1) % settings.reflection_interval == 0:
                self.reflect("periodic")
                generated = len([r for r in results if r.get("success")])
                logger.info(f"Progress: {generated} generated, {skipped} skipped, {i + 1}/{len(articles)} processed")
        
        # Final summary
        generated = len([r for r in results if r.get("success")])
        logger.info(f"📊 Final: {generated} articles generated, {skipped} duplicates skipped")
        
        return results
