"""Multi-agent orchestrator with metacognitive coordination"""
from typing import Dict, Any, List
from pathlib import Path
import logging
from datetime import datetime

from .agents.collector import CollectorAgent
from .agents.analyzer import AnalyzerAgent
from .agents.retriever import RetrieverAgent
from .agents.writer import WriterAgent
from .memory.base import MemoryStore, MemoryEntry, MemoryType
from .config import settings

logger = logging.getLogger(__name__)


class Orchestrator:
    """Coordinates multiple agents with metacognitive oversight"""
    
    def __init__(self):
        # Initialize shared memory
        memory_path = settings.memory_persist_dir / "shared_memory.db"
        self.shared_memory = MemoryStore(memory_path)
        
        # Initialize agents
        self.collector = CollectorAgent(self.shared_memory)
        self.analyzer = AnalyzerAgent(self.shared_memory)
        self.retriever = RetrieverAgent(self.shared_memory)
        self.writer = WriterAgent(self.shared_memory)
        
        self.agents = [self.collector, self.analyzer, self.retriever, self.writer]
        
        # Orchestrator's own metacognition
        self.execution_history: List[Dict[str, Any]] = []
        self.performance_metrics = {
            "total_runs": 0,
            "successful_runs": 0,
            "total_articles_collected": 0,
            "total_articles_retrieved": 0
        }
    
    def run_pipeline(self) -> Dict[str, Any]:
        """Execute the full news intelligence pipeline"""
        start_time = datetime.now()
        
        # CRITICAL: Use print() for guaranteed output in GitHub Actions
        print("\n" + "=" * 80)
        print("🚀 STARTING MULTI-AGENT NEWS INTELLIGENCE PIPELINE")
        print("=" * 80)
        
        logger.info("=" * 80)
        logger.info("🚀 Starting multi-agent news intelligence pipeline")
        logger.info("=" * 80)
        
        try:
            # Phase 1: Collection
            print("\n📰 PHASE 1: COLLECTION")
            print("-" * 80)
            print(f"Categories to collect: {settings.categories}")
            print(f"Pages per category: {settings.pages_per_category}")
            print(f"Page size: {settings.page_size}")
            
            logger.info("")
            logger.info("📰 PHASE 1: COLLECTION")
            logger.info("-" * 80)
            logger.info(f"Categories to collect: {settings.categories}")
            logger.info(f"Pages per category: {settings.pages_per_category}")
            logger.info(f"Page size: {settings.page_size}")
            
            print("🔄 Calling collector.collect_all_categories()...")
            collected = self.collector.collect_all_categories()
            print(f"✅ Collector returned: {type(collected)}, keys: {list(collected.keys()) if collected else 'None'}")
            
            all_articles = []
            for category, articles in collected.items():
                print(f"  Category '{category}': {len(articles)} articles")
                logger.info(f"  Category '{category}': {len(articles)} articles")
                all_articles.extend(articles)
            
            print(f"✅ Total collected: {len(all_articles)} unique articles")
            logger.info(f"✅ Total collected: {len(all_articles)} unique articles")
            
            if all_articles:
                print(f"📋 Sample article keys: {list(all_articles[0].keys())}")
                print(f"📋 Sample article title: {all_articles[0].get('title', 'NO TITLE')[:80]}")
                logger.info(f"Sample article: {all_articles[0] if all_articles else 'None'}")
            else:
                print("❌ WARNING: No articles collected!")
                logger.warning("No articles collected!")
            
            # Phase 2: Analysis
            print("\n🔍 PHASE 2: ANALYSIS")
            print("-" * 80)
            print(f"Analyzing first {min(50, len(all_articles))} articles")
            
            logger.info("")
            logger.info("🔍 PHASE 2: ANALYSIS")
            logger.info("-" * 80)
            logger.info(f"Analyzing first {min(50, len(all_articles))} articles")
            
            print("🔄 Calling analyzer.analyze_batch()...")
            analyses = self.analyzer.analyze_batch(all_articles[:50])
            print(f"✅ Analyzer returned: {len(analyses)} results")
            
            successful_analyses = [a for a in analyses if a.get("success")]
            failed_analyses = [a for a in analyses if not a.get("success")]
            
            print(f"✅ Successfully analyzed: {len(successful_analyses)}")
            print(f"❌ Failed analysis: {len(failed_analyses)}")
            
            logger.info(f"✅ Successfully analyzed: {len(successful_analyses)}")
            logger.info(f"❌ Failed analysis: {len(failed_analyses)}")
            
            if successful_analyses:
                print(f"📋 Sample successful analysis keys: {list(successful_analyses[0].keys())}")
                logger.info(f"Sample analysis: {successful_analyses[0]}")
            if failed_analyses:
                print(f"📋 Sample failure: {failed_analyses[0]}")
                logger.info(f"Sample failure: {failed_analyses[0]}")
            
            # Phase 3: Save (NEW LOGIC!)
            print("\n💾 PHASE 3: SAVING ARTICLES")
            print("-" * 80)
            print(f"Attempting to save {len(successful_analyses[:20])} analyzed articles")
            
            logger.info("")
            logger.info("💾 PHASE 3: SAVING ARTICLES")
            logger.info("-" * 80)
            logger.info(f"Attempting to save {len(successful_analyses[:20])} analyzed articles")
            
            print("🔄 Calling _save_analyzed_articles()...")
            generated = self._save_analyzed_articles(successful_analyses[:20])
            print(f"✅ Save function returned: {len(generated)} results")
            
            successful_generations = [g for g in generated if g.get("success")]
            failed_generations = [g for g in generated if not g.get("success")]
            
            print(f"\n✅ Successfully saved: {len(successful_generations)} articles")
            print(f"❌ Failed/Skipped: {len(failed_generations)} articles")
            
            logger.info("")
            logger.info(f"✅ Successfully saved: {len(successful_generations)} articles")
            logger.info(f"❌ Failed/Skipped: {len(failed_generations)} articles")
            
            if failed_generations:
                print("Failed/Skipped reasons:")
                logger.info("Failed/Skipped reasons:")
                for i, fail in enumerate(failed_generations[:5], 1):
                    reason = fail.get('error', 'Unknown error')
                    print(f"  {i}. {reason}")
                    logger.info(f"  {i}. {reason}")
            
            # Set retrieved count to match generated for metrics
            successful_retrievals = successful_generations
            
            # Metacognitive reflection
            self._reflect_on_execution(collected, analyses, successful_generations, [])
            
            # Update metrics
            self.performance_metrics["total_runs"] += 1
            self.performance_metrics["successful_runs"] += 1
            self.performance_metrics["total_articles_collected"] += len(all_articles)
            self.performance_metrics["total_articles_retrieved"] += len(successful_generations)  # Now same as generated
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            print(f"\n✨ Pipeline completed in {execution_time:.2f}s")
            print(f"📊 Final counts: collected={len(all_articles)}, analyzed={len(successful_analyses)}, saved={len(successful_generations)}")
            print("=" * 80 + "\n")
            
            logger.info(f"✨ Pipeline completed in {execution_time:.2f}s")
            
            result = {
                "success": True,
                "execution_time": execution_time,
                "collected_count": len(all_articles),
                "analyzed_count": len(successful_analyses),
                "retrieved_count": len(successful_generations),  # Same as generated now
                "generated_count": len(successful_generations),
                "agent_statuses": self.get_agent_statuses(),
                "performance_metrics": self.performance_metrics
            }
            
            # Store execution in memory
            self._store_execution(result)
            
            logger.info(f"✨ Pipeline completed in {execution_time:.2f}s")
            
            result = {
            
        except Exception as e:
            logger.error(f"❌ Pipeline failed: {e}")
            self.performance_metrics["total_runs"] += 1
            return {
                "success": False,
                "error": str(e),
                "agent_statuses": self.get_agent_statuses()
            }
    
    def _save_analyzed_articles(self, analyses: List[Dict]) -> List[Dict]:
        """Save analyzed articles with descriptions from NewsAPI (grounded content)"""
        print(f"\n🔧 _save_analyzed_articles called with {len(analyses)} articles")
        results = []
        
        # Get list of existing article titles to avoid duplicates
        print("🔍 Checking for existing articles...")
        existing_titles = self._get_existing_article_titles()
        print(f"📋 Found {len(existing_titles)} existing articles on site")
        
        logger.info(f"📋 Found {len(existing_titles)} existing articles on site")
        if existing_titles:
            print(f"📋 Existing titles: {existing_titles[:3]}...")
            logger.info(f"📋 Existing titles: {existing_titles[:3]}...")  # Show first 3
        
        print(f"📝 Processing {len(analyses)} articles for saving")
        logger.info(f"📝 Processing {len(analyses)} articles for saving")
        
        for i, article_data in enumerate(analyses, 1):
            try:
                # Extract article info from analysis
                title = article_data.get("title", "Untitled")
                description = article_data.get("description", "")
                content = article_data.get("content", "")
                url = article_data.get("url", "")
                source = article_data.get("source", "Unknown")
                published_at = article_data.get("published_at", "")
                keywords = article_data.get("keywords", [])
                query = article_data.get("query", "")
                
                print(f"[{i}/{len(analyses)}] Processing: {title[:60]}...")
                logger.info(f"[{i}/{len(analyses)}] Processing: {title[:60]}...")
                
                if not title:
                    print(f"[{i}/{len(analyses)}] ❌ No title found")
                    logger.warning(f"[{i}/{len(analyses)}] ❌ No title found")
                    results.append({"success": False, "error": "No title"})
                    continue
                
                # Check if article already exists on site
                if self._is_duplicate_title(title, existing_titles):
                    print(f"[{i}/{len(analyses)}] ⏭️  Skipping duplicate: {title[:50]}...")
                    logger.info(f"[{i}/{len(analyses)}] ⏭️  Skipping duplicate: {title[:50]}...")
                    results.append({"success": False, "error": "Duplicate article already on site"})
                    continue
                
                # Create markdown content with REAL article data from NewsAPI
                markdown = f"""# {title}

**Source:** {source}  
**Published:** {published_at}  
**URL:** {url}  
**Keywords:** {', '.join(keywords[:10])}

---

## Summary

{description if description else "No description available."}

---

## Content Preview

{content if content else "Full content available at source URL."}

---

## Key Topics

"""
                
                # Add keyword sections
                for i, keyword in enumerate(keywords[:5], 1):
                    markdown += f"{i}. **{keyword.title()}**\n"
                
                markdown += f"""

---

*This article was automatically curated from {source}.*  
*Original article: {url}*  
*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}*
"""
                
                # Save to file
                filename = self._sanitize_filename(title)
                filepath = settings.generated_articles_dir / f"{filename}.md"
                
                print(f"[{i}/{len(analyses)}] 💾 Saving to: {filepath.name}")
                
                # Ensure directory exists
                settings.generated_articles_dir.mkdir(parents=True, exist_ok=True)
                
                # Write file
                filepath.write_text(markdown, encoding='utf-8')
                
                print(f"[{i}/{len(analyses)}] ✅ File written successfully!")
                
                # Add to existing titles list to prevent duplicates within this batch
                existing_titles.append(title)
                
                results.append({
                    "success": True,
                    "title": title,
                    "filename": str(filepath)
                })
                
                print(f"[{i}/{len(analyses)}] ✅ Saved: {title[:60]}...")
                logger.info(f"[{i}/{len(analyses)}] ✅ Saved: {title[:60]}...")
                
            except Exception as e:
                print(f"[{i}/{len(analyses)}] ❌ Error saving article: {e}")
                logger.error(f"[{i}/{len(analyses)}] ❌ Error saving article: {e}")
                results.append({"success": False, "error": str(e)})
        
        print(f"\n🏁 _save_analyzed_articles completed: {len(results)} results")
        return results
    
    def _sanitize_filename(self, title: str) -> str:
        """Convert title to safe filename"""
        import re
        # Remove special characters
        safe = re.sub(r'[^\w\s-]', '', title)
        # Replace spaces with underscores
        safe = re.sub(r'[-\s]+', '_', safe)
        # Limit length
        safe = safe[:100]
        # Add timestamp to ensure uniqueness
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{safe}_{timestamp}"
    
    def _get_existing_article_titles(self) -> List[str]:
        """Get titles of all existing articles on the site"""
        existing_titles = []
        
        if not settings.generated_articles_dir.exists():
            return existing_titles
        
        # Read all markdown files in generated_articles directory
        for filepath in settings.generated_articles_dir.glob("*.md"):
            try:
                content = filepath.read_text(encoding='utf-8')
                # Extract title from markdown (first line starting with #)
                lines = content.split('\n')
                for line in lines:
                    if line.startswith('# '):
                        title = line[2:].strip()
                        existing_titles.append(title)
                        break
            except Exception as e:
                logger.warning(f"Error reading {filepath}: {e}")
        
        return existing_titles
    
    def _is_duplicate_title(self, new_title: str, existing_titles: List[str]) -> bool:
        """Check if title is duplicate using fuzzy matching"""
        from rapidfuzz import fuzz
        
        for existing_title in existing_titles:
            similarity = fuzz.token_sort_ratio(new_title, existing_title)
            if similarity >= settings.similarity_threshold:
                return True
        
        return False
    
    def _reflect_on_execution(self, collected: Dict, analyses: List, generated: List, _unused: List = []):
        """Metacognitive reflection on pipeline execution"""
        logger.info("🧠 Performing metacognitive reflection")
        
        # Trigger reflection in each agent
        for agent in self.agents:
            reflection = agent.reflect("pipeline_completion")
            logger.info(f"  {agent.name}: {len(reflection.insights)} insights generated")
        
        # Orchestrator-level insights
        collection_efficiency = sum(len(titles) for titles in collected.values()) / (
            len(collected) * settings.page_size * settings.pages_per_category
        )
        
        analysis_success_rate = sum(1 for a in analyses if a.get("success")) / max(1, len(analyses))
        generation_success_rate = sum(1 for g in generated if g.get("success")) / max(1, len(generated))
        
        insights = [
            f"Collection efficiency: {collection_efficiency:.2%}",
            f"Analysis success rate: {analysis_success_rate:.2%}",
            f"Article generation rate: {generation_success_rate:.2%}"
        ]
        
        for insight in insights:
            logger.info(f"  💡 {insight}")
        
        # Store orchestrator insights
        memory_entry = MemoryEntry(
            id=f"orchestrator_reflection_{datetime.now().timestamp()}",
            type=MemoryType.EPISODIC,
            content={
                "insights": insights,
                "collection_efficiency": collection_efficiency,
                "analysis_success_rate": analysis_success_rate,
                "generation_success_rate": generation_success_rate
            },
            timestamp=datetime.now(),
            importance=0.9
        )
        self.shared_memory.store(memory_entry)
    
    def _store_execution(self, result: Dict[str, Any]):
        """Store execution result in memory"""
        memory_entry = MemoryEntry(
            id=f"execution_{datetime.now().timestamp()}",
            type=MemoryType.EPISODIC,
            content=result,
            timestamp=datetime.now(),
            importance=0.8
        )
        self.shared_memory.store(memory_entry)
        self.execution_history.append(result)
    
    def get_agent_statuses(self) -> Dict[str, Any]:
        """Get status of all agents"""
        return {
            agent.name: agent.get_status()
            for agent in self.agents
        }
    
    def get_system_report(self) -> str:
        """Generate comprehensive system report"""
        report = []
        report.append("=" * 60)
        report.append("MULTI-AGENT NEWS INTELLIGENCE SYSTEM REPORT")
        report.append("=" * 60)
        report.append("")
        
        # Performance metrics
        report.append("📊 PERFORMANCE METRICS")
        report.append("-" * 60)
        for key, value in self.performance_metrics.items():
            report.append(f"  {key}: {value}")
        report.append("")
        
        # Agent statuses
        report.append("🤖 AGENT STATUSES")
        report.append("-" * 60)
        for agent in self.agents:
            status = agent.get_status()
            report.append(f"\n  {agent.name}:")
            report.append(f"    State: {status['state']}")
            report.append(f"    Success Rate: {status['success_rate']:.2%}")
            report.append(f"    Thoughts: {status['thoughts_count']}")
            report.append(f"    Actions: {status['actions_count']}")
            report.append(f"    Reflections: {status['reflections_count']}")
        report.append("")
        
        # Recent executions
        if self.execution_history:
            report.append("📜 RECENT EXECUTIONS")
            report.append("-" * 60)
            for i, exec_result in enumerate(self.execution_history[-5:], 1):
                report.append(f"\n  Execution {i}:")
                report.append(f"    Success: {exec_result.get('success')}")
                report.append(f"    Collected: {exec_result.get('collected_count', 0)}")
                report.append(f"    Retrieved: {exec_result.get('retrieved_count', 0)}")
                report.append(f"    Time: {exec_result.get('execution_time', 0):.2f}s")
        
        report.append("")
        report.append("=" * 60)
        
        return "\n".join(report)
