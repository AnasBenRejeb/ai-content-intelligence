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
        logger.info("🚀 Starting multi-agent news intelligence pipeline")
        
        try:
            # Phase 1: Collection
            logger.info("📰 Phase 1: Collecting news titles")
            collected = self.collector.collect_all_categories()
            
            all_titles = []
            for category, titles in collected.items():
                all_titles.extend(titles)
            
            logger.info(f"✅ Collected {len(all_titles)} unique titles")
            
            # Phase 2: Analysis
            logger.info("🔍 Phase 2: Analyzing titles and extracting keywords")
            analyses = self.analyzer.analyze_batch(all_titles[:50])  # Limit for demo
            
            successful_analyses = [a for a in analyses if a.get("success")]
            logger.info(f"✅ Analyzed {len(successful_analyses)} titles")
            
            # Phase 3: Retrieval
            logger.info("📥 Phase 3: Retrieving full articles")
            retrieved = self.retriever.retrieve_batch(successful_analyses[:20])  # Limit for demo
            
            successful_retrievals = [r for r in retrieved if r.get("success")]
            logger.info(f"✅ Retrieved {len(successful_retrievals)} articles")
            
            # Phase 4: Generation
            if settings.llm_enabled and successful_retrievals:
                logger.info("✍️  Phase 4: Generating new articles with LLM")
                generated = self.writer.generate_batch(successful_retrievals[:10])  # Limit for demo
                
                successful_generations = [g for g in generated if g.get("success")]
                logger.info(f"✅ Generated {len(successful_generations)} articles")
            else:
                generated = []
                successful_generations = []
                if not settings.llm_enabled:
                    logger.info("⏭️  Phase 4: Skipped (LLM disabled in config)")
            
            # Metacognitive reflection
            self._reflect_on_execution(collected, analyses, retrieved, generated if settings.llm_enabled else [])
            
            # Update metrics
            self.performance_metrics["total_runs"] += 1
            self.performance_metrics["successful_runs"] += 1
            self.performance_metrics["total_articles_collected"] += len(all_titles)
            self.performance_metrics["total_articles_retrieved"] += len(successful_retrievals)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            result = {
                "success": True,
                "execution_time": execution_time,
                "collected_count": len(all_titles),
                "analyzed_count": len(successful_analyses),
                "retrieved_count": len(successful_retrievals),
                "generated_count": len(successful_generations) if settings.llm_enabled else 0,
                "agent_statuses": self.get_agent_statuses(),
                "performance_metrics": self.performance_metrics
            }
            
            # Store execution in memory
            self._store_execution(result)
            
            logger.info(f"✨ Pipeline completed in {execution_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"❌ Pipeline failed: {e}")
            self.performance_metrics["total_runs"] += 1
            return {
                "success": False,
                "error": str(e),
                "agent_statuses": self.get_agent_statuses()
            }
    
    def _reflect_on_execution(self, collected: Dict, analyses: List, retrieved: List, generated: List = []):
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
        retrieval_success_rate = sum(1 for r in retrieved if r.get("success")) / max(1, len(retrieved))
        generation_success_rate = sum(1 for g in generated if g.get("success")) / max(1, len(generated)) if generated else 0
        
        insights = [
            f"Collection efficiency: {collection_efficiency:.2%}",
            f"Analysis success rate: {analysis_success_rate:.2%}",
            f"Retrieval success rate: {retrieval_success_rate:.2%}"
        ]
        
        if generated:
            insights.append(f"Generation success rate: {generation_success_rate:.2%}")
        
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
                "retrieval_success_rate": retrieval_success_rate
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
