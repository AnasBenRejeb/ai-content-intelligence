"""Article writer agent using Google Gemini API (FREE)"""
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
    """Agent responsible for generating articles using Gemini API"""
    
    def __init__(self, memory_store: MemoryStore, model_path: Optional[str] = None):
        super().__init__("WriterAgent", memory_store)
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        self.gemini_model = None
        self.generated_dir = settings.generated_articles_dir
        self.generated_dir.mkdir(parents=True, exist_ok=True)
        self.self_model["strengths"] = ["article_generation", "content_synthesis"]
        
        # Initialize Gemini API
        self._init_gemini()
    
    def _init_gemini(self):
        """Initialize Google Gemini API (FREE tier: 15 req/min, 1500/day)"""
        try:
            if not self.gemini_api_key:
                logger.warning("GEMINI_API_KEY not found in environment")
                logger.info("WriterAgent will operate in template mode")
                logger.info("Get free API key at: https://makersuite.google.com/app/apikey")
                return
            
            import google.generativeai as genai
            genai.configure(api_key=self.gemini_api_key)
            
            # Use Gemini 1.5 Flash (free tier, fast, good quality)
            self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
            logger.info("✅ Gemini API initialized successfully (FREE tier)")
            
        except ImportError:
            logger.warning("google-generativeai not installed. Install with: pip install google-generativeai")
            logger.info("WriterAgent will operate in template mode")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini API: {e}")
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
                    "has_gemini": self.gemini_model is not None,
                    "skip_duplicate": True,
                    "previous_generation": already_generated
                }
            )
        
        # Check if we have Gemini API
        if self.gemini_model:
            reasoning.append("Using Gemini API for AI rewriting")
            confidence = 0.90
        else:
            reasoning.append("Using template-based generation (Gemini API not available)")
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
                "has_gemini": self.gemini_model is not None,
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
                "use_gemini": thought.metadata["has_gemini"],
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
            
            if action.parameters["use_gemini"] and self.gemini_model:
                article = self._generate_with_gemini(title, description, source_content, source, source_url, keywords)
            else:
                article = self._generate_template(title, source, source_url, keywords)
            
            if article:
                # Save generated article
                saved_path = self._save_article(title, article)
                
                result = {
                    "success": True,
                    "title": title,
                    "article": article,
                    "word_count": len(article.split()),
                    "path": str(saved_path),
                    "method": "gemini" if action.parameters["use_gemini"] else "template",
                    "source_url": source_url
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
    
    def _generate_with_gemini(self, title: str, description: str, source_content: str, 
                             source: str, source_url: str, keywords: List[str]) -> str:
        """Generate AI-rewritten article using Gemini API with agentic thinking patterns"""
        try:
            logger.info("🧠 STEP 1: Metacognitive Analysis - Understanding the task")
            
            # STEP 1: THINK - Analyze what makes a good article (like NYT, BBC, Reuters)
            analysis_prompt = f"""You are an expert content strategist at a top news organization (like NYT, BBC, Reuters).

Analyze this news story and create a content strategy:

Original Title: {title}
Source: {source}
Description: {description}
Keywords: {', '.join(keywords[:5])}

Think step-by-step:
1. What's the CORE story here? (one sentence)
2. What angle would make this compelling for readers?
3. What's a better, more engaging title? (10 words max, clickable but not clickbait)
4. What structure would work best? (inverted pyramid, narrative, analysis)
5. What tone? (informative, analytical, urgent, explanatory)

Provide your analysis in this format:
CORE STORY: [one sentence]
ANGLE: [the unique perspective]
BETTER TITLE: [improved title]
STRUCTURE: [article structure]
TONE: [writing tone]"""

            logger.info("🤔 Asking Gemini to analyze the story...")
            analysis_response = self.gemini_model.generate_content(analysis_prompt)
            analysis = analysis_response.text.strip()
            logger.info(f"✅ Analysis complete:\n{analysis[:200]}...")
            
            # Extract the better title from analysis
            better_title = title  # fallback
            for line in analysis.split('\n'):
                if line.startswith('BETTER TITLE:'):
                    better_title = line.replace('BETTER TITLE:', '').strip()
                    break
            
            logger.info(f"📝 Original title: {title}")
            logger.info(f"✨ Improved title: {better_title}")
            
            # STEP 2: PLAN - Create article outline
            outline_prompt = f"""Based on this analysis:

{analysis}

Original content preview: {source_content[:500]}

Create a detailed outline for a 400-500 word article. Include:
- Hook/Lead (what grabs attention)
- 3-4 main points to cover
- Key facts to include
- Conclusion angle

Format as:
HOOK: [compelling opening]
POINT 1: [main point]
POINT 2: [main point]
POINT 3: [main point]
CONCLUSION: [takeaway]"""

            logger.info("📋 Creating article outline...")
            outline_response = self.gemini_model.generate_content(outline_prompt)
            outline = outline_response.text.strip()
            logger.info(f"✅ Outline created:\n{outline[:200]}...")
            
            # STEP 3: WRITE - Generate the actual article
            writing_prompt = f"""You are a professional journalist at a top news organization.

Write a complete, original article following this plan:

TITLE: {better_title}
ANALYSIS: {analysis}
OUTLINE: {outline}

CRITICAL RULES:
1. Write in YOUR OWN WORDS - do NOT copy the source
2. Make it engaging and readable (like NYT, BBC, Reuters style)
3. Use active voice and clear language
4. Include specific facts from the source
5. 400-500 words
6. Professional journalistic tone
7. No fluff - every sentence adds value

Write the article now (body only, no title):"""

            logger.info("✍️  Writing the article...")
            article_response = self.gemini_model.generate_content(writing_prompt)
            article_body = article_response.text.strip()
            logger.info(f"✅ Article written: {len(article_body.split())} words")
            
            # STEP 4: REVIEW - Self-critique and improve
            review_prompt = f"""You are an editor at a top news organization.

Review this article and suggest ONE specific improvement:

TITLE: {better_title}
ARTICLE: {article_body[:500]}...

What's the ONE most important improvement? (be specific and brief)"""

            logger.info("🔍 Self-reviewing the article...")
            review_response = self.gemini_model.generate_content(review_prompt)
            review = review_response.text.strip()
            logger.info(f"💡 Self-critique: {review[:100]}...")
            
            # STEP 5: FORMAT - Create final markdown with attribution
            article = f"""# {better_title}

*Original story from {source} | AI-rewritten for clarity and engagement*

{article_body}

---

**📰 Source & Attribution**  
Original article: [{source}]({source_url})  
Topics: {', '.join(keywords[:5])}  
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}

*This article was rewritten by AI based on the original source. All facts and information are attributed to {source}. This is for educational and informational purposes.*
"""
            
            word_count = len(article_body.split())
            logger.info(f"✅ Final article: {word_count} words, title improved, professionally written")
            
            return article
            
        except Exception as e:
            logger.error(f"Gemini API generation failed: {e}")
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
