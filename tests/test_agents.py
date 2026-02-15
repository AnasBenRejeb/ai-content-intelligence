"""Tests for agent system"""
import pytest
from pathlib import Path
from src.memory.base import MemoryStore
from src.agents.collector import CollectorAgent
from src.agents.analyzer import AnalyzerAgent
from src.agents.retriever import RetrieverAgent


@pytest.fixture
def memory_store(tmp_path):
    """Create temporary memory store"""
    return MemoryStore(tmp_path / "test_memory.db")


def test_collector_agent(memory_store):
    """Test collector agent"""
    agent = CollectorAgent(memory_store)
    
    # Test thinking
    thought = agent.think({"category": "technology"})
    assert thought.confidence > 0
    assert len(thought.reasoning) > 0
    
    # Test status
    status = agent.get_status()
    assert status["name"] == "CollectorAgent"
    assert status["thoughts_count"] == 1


def test_analyzer_agent(memory_store):
    """Test analyzer agent"""
    agent = AnalyzerAgent(memory_store)
    
    # Test analysis
    title = "AI breakthrough in medical diagnosis"
    thought = agent.think({"title": title})
    result = agent.act(thought)
    
    assert result["success"]
    assert "keywords" in result
    assert len(result["keywords"]) > 0


def test_retriever_agent(memory_store, tmp_path):
    """Test retriever agent"""
    agent = RetrieverAgent(memory_store)
    agent.articles_dir = tmp_path / "articles"
    agent.articles_dir.mkdir()
    
    # Test thinking
    thought = agent.think({
        "title": "Test Article",
        "query": "test query"
    })
    
    assert thought.confidence > 0
    assert "Test Article" in thought.content


def test_agent_reflection(memory_store):
    """Test agent reflection"""
    agent = CollectorAgent(memory_store)
    
    # Perform some actions
    for i in range(5):
        thought = agent.think({"category": "technology"})
        agent.act(thought)
    
    # Trigger reflection
    reflection = agent.reflect("test")
    
    assert len(reflection.observations) > 0
    assert len(agent.reflections) == 1


def test_agent_learning(memory_store):
    """Test agent learning"""
    agent = AnalyzerAgent(memory_store)
    
    # Learn from experience
    agent.learn({
        "action": "extract_keywords",
        "success": True,
        "keyword_count": 5
    })
    
    assert len(agent.self_model["learned_patterns"]) > 0
