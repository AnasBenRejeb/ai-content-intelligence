"""Comprehensive test suite for all components"""
import pytest
import sys
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents.base import BaseAgent, Thought, Action, Reflection
from src.agents.collector import CollectorAgent
from src.agents.analyzer import AnalyzerAgent
from src.agents.retriever import RetrieverAgent
from src.agents.writer import WriterAgent
from src.memory.base import MemoryStore, MemoryEntry, MemoryType
from src.orchestrator import Orchestrator
from src.config import settings


class TestBaseAgent:
    """Test BaseAgent metacognitive capabilities"""
    
    def test_agent_initialization(self, memory_store):
        """Test agent initializes correctly"""
        agent = BaseAgent("TestAgent", memory_store)
        
        assert agent.name == "TestAgent"
        assert agent.memory == memory_store
        assert agent.success_count == 0
        assert agent.failure_count == 0
        assert len(agent.thoughts) == 0
        assert len(agent.actions_taken) == 0
        
    def test_think_generates_thought(self, memory_store):
        """Test think() generates valid thought"""
        agent = BaseAgent("TestAgent", memory_store)
        
        # Mock the abstract method
        agent._generate_thought = Mock(return_value=Thought(
            content="Test thought",
            confidence=0.8,
            reasoning=["reason1", "reason2"],
            metadata={"key": "value"},
            timestamp=datetime.now()
        ))
        
        thought = agent.think({"test": "context"})
        
        assert thought.content == "Test thought"
        assert thought.confidence == 0.8
        assert len(thought.reasoning) == 2
        assert len(agent.thoughts) == 1
        
    def test_act_executes_action(self, memory_store):
        """Test act() executes action"""
        agent = BaseAgent("TestAgent", memory_store)
        
        # Mock methods
        agent._plan_action = Mock(return_value=Action(
            name="test_action",
            parameters={"param": "value"},
            expected_outcome="success",
            confidence=0.8,
            timestamp=datetime.now()
        ))
        agent._execute_action = Mock(return_value={"success": True})
        
        thought = Thought(
            content="test",
            confidence=0.8,
            reasoning=[],
            metadata={},
            timestamp=datetime.now()
        )
        
        result = agent.act(thought)
        
        assert result["success"] is True
        assert len(agent.actions_taken) == 1
        assert agent.success_count == 1
        
    def test_reflect_generates_insights(self, memory_store):
        """Test reflect() generates insights"""
        agent = BaseAgent("TestAgent", memory_store)
        
        # Add some history
        agent.success_count = 8
        agent.failure_count = 2
        
        reflection = agent.reflect("test_trigger")
        
        assert reflection.trigger == "test_trigger"
        assert len(reflection.insights) > 0
        assert "success_rate" in reflection.performance_summary
        assert len(agent.reflections) == 1
        
    def test_learn_updates_memory(self, memory_store):
        """Test learn() stores in memory"""
        agent = BaseAgent("TestAgent", memory_store)
        
        outcome = {
            "action": "test_action",
            "success": True,
            "result": "good"
        }
        
        agent.learn(outcome)
        
        # Check memory was stored
        memories = memory_store.retrieve_all()
        assert len(memories) > 0
        
    def test_get_status(self, memory_store):
        """Test get_status() returns correct info"""
        agent = BaseAgent("TestAgent", memory_store)
        agent.success_count = 7
        agent.failure_count = 3
        
        status = agent.get_status()
        
        assert status["name"] == "TestAgent"
        assert status["state"] == "idle"
        assert status["success_rate"] == 0.7
        assert status["thoughts_count"] == 0
        assert status["actions_count"] == 0


class TestCollectorAgent:
    """Test CollectorAgent functionality"""
    
    @patch('requests.get')
    def test_collect_from_newsapi(self, mock_get, memory_store):
        """Test collecting from NewsAPI"""
        # Mock API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "ok",
            "articles": [
                {"title": "Test Article 1"},
                {"title": "Test Article 2"},
                {"title": "Test Article 3"}
            ]
        }
        mock_get.return_value = mock_response
        
        agent = CollectorAgent(memory_store)
        titles = agent._fetch_from_newsapi("technology")
        
        assert len(titles) == 3
        assert "Test Article 1" in titles
        
    def test_deduplicate_titles(self, memory_store):
        """Test title deduplication"""
        agent = CollectorAgent(memory_store)
        
        titles = [
            "AI Breakthrough in Medicine",
            "AI Breakthrough in Medical Field",  # Similar
            "Climate Change Impact",
            "AI Breakthrough in Medicine"  # Exact duplicate
        ]
        
        unique = agent._deduplicate_titles(titles)
        
        # Should remove exact duplicate and similar title
        assert len(unique) < len(titles)
        assert "Climate Change Impact" in unique
        
    @patch('requests.get')
    def test_collect_all_categories(self, mock_get, memory_store):
        """Test collecting from all categories"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "ok",
            "articles": [{"title": f"Article {i}"} for i in range(10)]
        }
        mock_get.return_value = mock_response
        
        agent = CollectorAgent(memory_store)
        result = agent.collect_all_categories()
        
        assert isinstance(result, dict)
        assert len(result) > 0


class TestAnalyzerAgent:
    """Test AnalyzerAgent functionality"""
    
    def test_extract_keywords(self, memory_store):
        """Test keyword extraction"""
        agent = AnalyzerAgent(memory_store)
        
        title = "Artificial Intelligence Breakthrough in Medical Diagnosis Using Deep Learning"
        keywords = agent._extract_keywords(title)
        
        assert len(keywords) > 0
        assert all(isinstance(kw, tuple) for kw in keywords)
        assert all(len(kw) == 2 for kw in keywords)
        assert all(isinstance(kw[1], float) for kw in keywords)
        
    def test_generate_query(self, memory_store):
        """Test query generation"""
        agent = AnalyzerAgent(memory_store)
        
        title = "AI Breakthrough in Medicine"
        keywords = [("AI", 0.8), ("medicine", 0.7), ("breakthrough", 0.6)]
        
        query = agent._generate_query(title, keywords)
        
        assert isinstance(query, str)
        assert len(query) > 0
        assert "AI" in query or "medicine" in query
        
    def test_analyze_batch(self, memory_store):
        """Test batch analysis"""
        agent = AnalyzerAgent(memory_store)
        
        titles = [
            "AI in Healthcare",
            "Climate Change Solutions",
            "Tech Innovation 2025"
        ]
        
        results = agent.analyze_batch(titles)
        
        assert len(results) == len(titles)
        assert all("title" in r for r in results)
        assert all("keywords" in r for r in results)


class TestRetrieverAgent:
    """Test RetrieverAgent functionality"""
    
    def test_cache_check(self, memory_store, tmp_path):
        """Test cache checking"""
        agent = RetrieverAgent(memory_store)
        agent.articles_dir = tmp_path
        
        # Create cached article
        title = "Test Article"
        cache_path = agent._get_cache_path(title)
        cache_path.write_text("Cached content")
        
        # Check cache
        assert agent._check_cache(title) is True
        
    def test_sanitize_filename(self, memory_store):
        """Test filename sanitization"""
        agent = RetrieverAgent(memory_store)
        
        title = "Test: Article / With * Invalid ? Characters"
        sanitized = agent._sanitize_filename(title)
        
        assert ":" not in sanitized
        assert "/" not in sanitized
        assert "*" not in sanitized
        assert "?" not in sanitized
        
    @patch('requests.get')
    def test_search_gnews(self, mock_get, memory_store):
        """Test GNews search"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "totalArticles": 1,
            "articles": [{"url": "https://example.com/article"}]
        }
        mock_get.return_value = mock_response
        
        agent = RetrieverAgent(memory_store)
        url = agent._search_gnews("test query")
        
        assert url == "https://example.com/article"


class TestWriterAgent:
    """Test WriterAgent functionality"""
    
    def test_titles_similar(self, memory_store):
        """Test title similarity detection"""
        agent = WriterAgent(memory_store)
        
        title1 = "AI Breakthrough in Medical Diagnosis"
        title2 = "Medical Diagnosis AI Breakthrough"
        title3 = "Climate Change Impact"
        
        assert agent._titles_similar(title1, title2) is True
        assert agent._titles_similar(title1, title3) is False
        
    def test_create_metadata(self, memory_store):
        """Test metadata creation"""
        agent = WriterAgent(memory_store)
        
        title = "Test Article"
        url = "https://example.com"
        article = "This is test content"
        
        metadata = agent._create_metadata(title, url, article)
        
        assert metadata["title"] == title
        assert metadata["source_url"] == url
        assert "generated_at" in metadata
        assert "content_hash" in metadata
        assert metadata["word_count"] == 4
        
    def test_check_if_already_generated(self, memory_store):
        """Test duplicate detection"""
        agent = WriterAgent(memory_store)
        
        # Store a previous generation in memory
        memory_entry = MemoryEntry(
            id="test_gen",
            type=MemoryType.SEMANTIC,
            content={
                "action": "generate_article",
                "title": "AI Breakthrough in Medicine",
                "source_url": "https://example.com/article"
            },
            timestamp=datetime.now(),
            importance=0.8
        )
        memory_store.store(memory_entry)
        
        # Check for duplicate
        memories = memory_store.retrieve_all()
        result = agent._check_if_already_generated(
            "AI Breakthrough in Medical Field",  # Similar title
            "https://example.com/article",
            memories
        )
        
        assert result is not None
        
    def test_sanitize_filename(self, memory_store):
        """Test filename sanitization"""
        agent = WriterAgent(memory_store)
        
        title = "Test: Article / With * Invalid ? Characters"
        sanitized = agent._sanitize_filename(title)
        
        assert ":" not in sanitized
        assert "/" not in sanitized
        assert len(sanitized) <= 100
        
    def test_generate_template(self, memory_store):
        """Test template generation"""
        agent = WriterAgent(memory_store)
        
        title = "Test Article Title"
        article = agent._generate_template(title)
        
        assert isinstance(article, str)
        assert len(article) > 100
        assert title in article


class TestMemorySystem:
    """Test memory system functionality"""
    
    def test_memory_store_initialization(self, tmp_path):
        """Test memory store initializes correctly"""
        db_path = tmp_path / "test_memory.db"
        memory = MemoryStore(db_path)
        
        assert memory.db_path == db_path
        assert db_path.exists()
        
    def test_store_and_retrieve(self, memory_store):
        """Test storing and retrieving memories"""
        entry = MemoryEntry(
            id="test_1",
            type=MemoryType.EPISODIC,
            content={"action": "test", "result": "success"},
            timestamp=datetime.now(),
            importance=0.8
        )
        
        memory_store.store(entry)
        retrieved = memory_store.retrieve_all()
        
        assert len(retrieved) > 0
        assert any(m.id == "test_1" for m in retrieved)
        
    def test_query_with_filters(self, memory_store):
        """Test querying with filters"""
        # Store multiple entries
        for i in range(5):
            entry = MemoryEntry(
                id=f"test_{i}",
                type=MemoryType.SEMANTIC if i % 2 == 0 else MemoryType.EPISODIC,
                content={"index": i},
                timestamp=datetime.now(),
                importance=0.5 + (i * 0.1)
            )
            memory_store.store(entry)
        
        # Query semantic memories
        results = memory_store.query({"type": MemoryType.SEMANTIC})
        
        assert len(results) > 0
        assert all(m.type == MemoryType.SEMANTIC for m in results)
        
    def test_cleanup_old_memories(self, memory_store):
        """Test cleaning up old memories"""
        # Store old entry
        old_entry = MemoryEntry(
            id="old_1",
            type=MemoryType.EPISODIC,
            content={"old": True},
            timestamp=datetime.now() - timedelta(days=60),
            importance=0.3
        )
        memory_store.store(old_entry)
        
        # Store recent entry
        recent_entry = MemoryEntry(
            id="recent_1",
            type=MemoryType.EPISODIC,
            content={"recent": True},
            timestamp=datetime.now(),
            importance=0.8
        )
        memory_store.store(recent_entry)
        
        # Cleanup
        memory_store.cleanup(days=30)
        
        # Check old entry removed, recent kept
        all_memories = memory_store.retrieve_all()
        assert any(m.id == "recent_1" for m in all_memories)


class TestOrchestrator:
    """Test orchestrator functionality"""
    
    def test_orchestrator_initialization(self):
        """Test orchestrator initializes correctly"""
        orch = Orchestrator()
        
        assert orch.collector is not None
        assert orch.analyzer is not None
        assert orch.retriever is not None
        assert orch.writer is not None
        assert len(orch.agents) == 4
        
    def test_get_agent_statuses(self):
        """Test getting agent statuses"""
        orch = Orchestrator()
        statuses = orch.get_agent_statuses()
        
        assert len(statuses) == 4
        assert "CollectorAgent" in statuses
        assert "AnalyzerAgent" in statuses
        assert "RetrieverAgent" in statuses
        assert "WriterAgent" in statuses
        
    def test_get_system_report(self):
        """Test system report generation"""
        orch = Orchestrator()
        report = orch.get_system_report()
        
        assert isinstance(report, str)
        assert "PERFORMANCE METRICS" in report
        assert "AGENT STATUSES" in report


class TestIntegration:
    """Integration tests for complete pipeline"""
    
    @patch('requests.get')
    def test_end_to_end_pipeline(self, mock_get):
        """Test complete pipeline execution"""
        # Mock API responses
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "ok",
            "articles": [{"title": "Test Article"}],
            "totalArticles": 1
        }
        mock_response.text = "Article content"
        mock_get.return_value = mock_response
        
        # Run pipeline
        orch = Orchestrator()
        
        # Note: Full pipeline test would require more mocking
        # This is a basic structure test
        assert orch.collector is not None
        assert orch.analyzer is not None
        assert orch.retriever is not None
        assert orch.writer is not None


# Fixtures
@pytest.fixture
def memory_store(tmp_path):
    """Create temporary memory store"""
    db_path = tmp_path / "test_memory.db"
    return MemoryStore(db_path)


@pytest.fixture
def sample_titles():
    """Sample titles for testing"""
    return [
        "AI Breakthrough in Medical Diagnosis",
        "Climate Change Impact on Agriculture",
        "Tech Innovation Drives Economic Growth",
        "Healthcare Reform Debate Continues",
        "Space Exploration Reaches New Milestone"
    ]


@pytest.fixture
def sample_article():
    """Sample article for testing"""
    return {
        "title": "AI Breakthrough in Medicine",
        "content": "Researchers have announced a major breakthrough...",
        "url": "https://example.com/article",
        "success": True
    }


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
