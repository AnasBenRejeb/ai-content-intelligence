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
            
            # Phase 3: AI Generation (FOCUS HERE!)
            print("\n✍️  PHASE 3: AI ARTICLE GENERATION")
            print("-" * 80)
            print(f"Generating AI-rewritten articles with improved titles for {min(20, len(successful_analyses))} articles")
            
            logger.info("")
            logger.info("✍️  PHASE 3: AI ARTICLE GENERATION")
            logger.info("-" * 80)
            logger.info(f"Generating AI-rewritten articles for {min(20, len(successful_analyses))} articles")
            
            print("🔄 Calling writer.generate_batch()...")
            print("🤖 Writer will: Analyze → Plan → Write → Review → Format")
            generated = self.writer.generate_batch(successful_analyses[:20])
            print(f"✅ Writer returned: {len(generated)} results")
            
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
            self._reflect_on_execution(collected, analyses, generated, [])
            
            # Update metrics
            self.performance_metrics["total_runs"] += 1
            self.performance_metrics["successful_runs"] += 1
            self.performance_metrics["total_articles_collected"] += len(all_articles)
            self.performance_metrics["total_articles_retrieved"] += len(successful_generations)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            print(f"\n✨ Pipeline completed in {execution_time:.2f}s")
            print(f"📊 Final counts: collected={len(all_articles)}, analyzed={len(successful_analyses)}, generated={len(successful_generations)}")
            print("=" * 80 + "\n")
            
            logger.info(f"✨ Pipeline completed in {execution_time:.2f}s")
            
            result = {
                "success": True,
                "execution_time": execution_time,
                "collected_count": len(all_articles),
                "analyzed_count": len(successful_analyses),
                "retrieved_count": len(successful_generations),
                "generated_count": len(successful_generations),
                "agent_statuses": self.get_agent_statuses(),
                "performance_metrics": self.performance_metrics
            }
            
            # Store execution in memory
            self._store_execution(result)
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Pipeline failed: {e}")
            self.performance_metrics["total_runs"] += 1
            return {
                "success": False,
                "error": str(e),
                "agent_statuses": self.get_agent_statuses()
            }
    
    def _reflect_on_execution(self, collected: Dict, analyses: List, generated: List, _unused: List):
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
