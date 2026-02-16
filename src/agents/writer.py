"""Article writer agent using Gemini API or local LLM"""
from typing import Dict, Any, List, Optional
from pathlib import Path
import logging
from rapidfuzz import fuzz
import os
from datetime import datetime

from .base import BaseAgent, Thought, Action
from ..memory.base import MemoryStore, MemoryEntry, MemoryType
from ..config import settings

logger = logging.getLogger(__name__)


class WriterAgent(BaseAgent):
    """Agent responsible for generating articles using Gemini API or local LLM"""
    
    def __init__(self, memory_store: MemoryStore, model_path: Optional[str] = None):
        super().__init__("WriterAgent", memory_store)
        self.llm = None
        self.gemini_model = None
        self.model_path = Path(model_path) if model_path else settings.llm_model_path
        self.generated_dir = settings.generated_articles_dir
        self.generated_dir.mkdir(parents=True, exist_ok=True)
        self.self_model["strengths"] = ["article_generation", "content_synthesis"]
        
        # Try Gemini first, then local LLM
        self._init_gemini()
        if not self.gemini_model:
            self._init_llm()
    
    def _init_gemini(self):
        """Initialize Gemini API"""
        try:
            gemini_key = os.environ.get('GEMINI_API_KEY', '')
            if not gemini_key:
                logger.info("GEMINI_API_KEY not found - will try local LLM")
                return
            
            import google.generativeai as genai
            genai.configure(api_key=gemini_key)
            self.gemini_model = genai.GenerativeModel('gemini-pro')
            logger.info("✅ Gemini API initialized successfully")
            
        except ImportError:
            logger.warning("google-generativeai not installed. Install with: pip install google-generativeai")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini: {e}")
    
    def _init_llm(self):
        """Initialize local Llama.cpp LLM"""
        try:
            if not settings.llm_enabled:
                logger.info("LLM disabled in config - WriterAgent will use template mode")
                return
            
            if not self.model_path.exists():
                logger.warning(f"LLM model not found at {self.model_path}")
                logger.info("WriterAgent will operate in template mode")
                logger.info(f"Expected model: {self.model_path}")
                return
            
            from llama_cpp import Llama
            
            logger.info(f"Loading LLM model from {self.model_path}...")
            self.llm = Llama(
                model_path=str(self.model_path),
                n_ctx=4096,  # Context window
                n_threads=4,  # CPU threads
                verbose=False
            )
            logger.info("✅ Local LLM initialized successfully (Mistral-7B)")
            
        except ImportError:
            logger.warning("llama-cpp-python not installed. Install with: pip install llama-cpp-python")
            logger.info("WriterAgent will operate in template mode")
        except Exception as e:
            logger.error(f"Failed to initialize LLM: {e}")
            logger.info("WriterAgent will operate in template mode")
    
    def _generate_thought(self, context: Dict[str, Any], 
                         memories: List[MemoryEntry]) -> Thought:
        """Generate thought about article generation"""
        title = context.get("title", "")
        source_content = context.get("content", "")
        source_url = context.get("url", "")
        description = context.get("description", "")
        source = context.get("source", "Unknown")
        keywords = context.get("keywords", [])
        
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
        
        # Check if we have local LLM
        if self.llm:
            reasoning.append("Using local LLM (Mistral-7B) for AI rewriting")
            confidence = 0.90
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
                "source_url": source_url,
                "source_content": source_content,
                "description": description,
                "source": source,
                "keywords": keywords
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
                "source_url": thought.metadata.get("source_url", ""),
                "source_content": thought.metadata.get("source_content", ""),
                "description": thought.metadata.get("description", ""),
                "source": thought.metadata.get("source", "Unknown"),
                "keywords": thought.metadata.get("keywords", [])
            },
            expected_outcome="Generate unique AI-rewritten article",
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
            source_content = action.parameters.get("source_content", "")
            description = action.parameters.get("description", "")
            source = action.parameters.get("source", "Unknown")
            keywords = action.parameters.get("keywords", [])
            
            if action.parameters["use_llm"] and self.llm:
                article = self._generate_with_llm(title, description, source_content, source, source_url, keywords)
            else:
                article = self._generate_template(title, source, source_url, keywords)
            
            if article:
                # Save generated article
                saved_path = self._save_article(title, article)
                
                # Create metadata
                metadata = self._create_metadata(title, source_url, article)
                
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
                
                # Store in memory
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
    
    def _generate_with_llm(self, title: str, description: str, source_content: str, 
                          source: str, source_url: str, keywords: List[str]) -> str:
        """Generate satirical article using local LLM with agentic design patterns"""
        try:
            logger.info("🧠 AGENTIC ARTICLE GENERATION - Using Reflection + Planning + Execution")
            
            # Combine all source information
            news_content = f"{title}\n\n{description}\n\n{source_content[:1000]}"
            
            # AGENTIC PATTERN: Create satirical article with self-reflection
            satirical_prompt = f"""Write a wildly exaggerated, sarcastic, and rage-filled satirical reaction to the following news. Make it dramatic, over-the-top, and absurdly funny. Pretend this event is the most catastrophic, civilization-ending disaster ever, even if it's something trivial. Apply these techniques:

- **Hyperbole**: Exaggerate everything beyond reason.
- **Irony & Sarcasm**: Say the opposite of what you mean with biting humor.
- **Absurd Comparisons**: Compare the event to unrelated but massive disasters.
- **Personification**: Give objects or ideas human qualities.
- **Doomsday Language**: Make it sound like the apocalypse.
- **Incongruity**: Use a serious tone for ridiculous statements.
- **Mocking Self-Seriousness**: Treat this as world-changing when it's not.
- **Comic Rage**: Write as if you're irrationally furious.
- **Escalation**: Start small and spiral into chaos.
- **Rule of Three**: Use lists with an absurd twist.
- **Fake Expert Quotes**: Invent fake authorities saying ridiculous things.
- **False Cause**: Pretend this leads to insane consequences.

Rules:
- Do not copy or repeat text from the paragraph.
- Keep it general—do not tie it to real-world politics, ideologies, or specific movements unless mentioned in the text.
- Use dramatic metaphors, sarcastic humor, and absurd punchlines throughout.
- Write in full sentences like a news article, not bullet points.
- Write 400-500 words.

News:
{news_content}

Write your satirical article now:"""

            logger.info("✍️  Generating satirical content with LLM...")
            
            # Generate with LLM
            response = self.llm(
                satirical_prompt,
                max_tokens=1024,  # ~400-500 words
                temperature=0.8,  # Higher creativity for satire
                top_p=0.95,
                stop=["</s>", "\n\nNews:", "\n\nWrite"]
            )
            
            article_body = response['choices'][0]['text'].strip()
            word_count = len(article_body.split())
            logger.info(f"✅ Generated satirical article: {word_count} words")
            
            # AGENTIC PATTERN: Self-Reflection - Check quality
            logger.info("🔍 SELF-REFLECTION: Evaluating article quality...")
            reflection_prompt = f"""You are an editor reviewing a satirical article. Rate it 1-10 on:
- Humor/Satire quality
- Originality (not copying source)
- Engagement level

Article excerpt: {article_body[:300]}...

Rating (just number 1-10):"""
            
            reflection = self.llm(
                reflection_prompt,
                max_tokens=10,
                temperature=0.3
            )
            
            rating_text = reflection['choices'][0]['text'].strip()
            logger.info(f"💡 Self-reflection rating: {rating_text}/10")
            
            # Format final article with attribution
            article = f"""# {title}

*Satirical Commentary | Original story from {source}*

{article_body}

---

**📰 Source & Attribution**  
Original article: [{source}]({source_url})  
Topics: {', '.join(keywords[:5])}  
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}

*This is a satirical/sarcastic commentary based on real news from {source}. All facts are attributed to the original source. This content is for entertainment and commentary purposes.*
"""
            
            logger.info(f"✅ Final article complete: {len(article.split())} total words")
            return article
            
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            logger.info("Falling back to template mode")
            return self._generate_template(title, source, source_url, keywords)
    
    def _generate_template(self, title: str, source: str = "Unknown", 
                          source_url: str = "", keywords: List[str] = []) -> str:
        """Generate article using template (fallback when Gemini unavailable)"""
        article = f"""# {title}

*News summary from {source}*

## Overview

This article discusses {title.lower()}, covering key developments and implications in this area.

## Key Points

Recent reports indicate significant developments related to this topic. The situation continues to evolve as stakeholders monitor the latest updates.

## Context

Understanding the broader context helps frame the importance of these developments and their potential impact on various sectors.

## Looking Ahead

As this story develops, further updates and analysis will provide additional clarity on the implications and next steps.

---

**Source Attribution:**  
Original article: [{source}]({source_url})  
Keywords: {', '.join(keywords[:5])}  

*This is a summary based on news from {source}. Visit the original source for complete details.*
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
