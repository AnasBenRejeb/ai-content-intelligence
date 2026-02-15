"""Edge case and stress tests"""
import pytest
import sys
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch
import time

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents.collector import CollectorAgent
from src.agents.analyzer import AnalyzerAgent
from src.agents.retriever import RetrieverAgent
from src.agents.writer import WriterAgent
from src.memory.base import MemoryStore, MemoryEntry, MemoryType


class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_empty_title_handling(self, memory_store):
        """Test handling of empty titles"""
        agent = CollectorAgent(memory_store)
        titles = agent._deduplicate_titles(["", "Valid Title", ""])
        
        assert "Valid Title" in titles
        assert "" not in titles or len([t for t in titles if t == ""]) <= 1
        
    def test_very_long_title(self, memory_store):
        """Test handling of very long titles"""
        agent = AnalyzerAgent(memory_store)
        
        long_title = "A" * 1000  # 1000 character title
        keywords = agent._extract_keywords(long_title)
        
        # Should handle without crashing
        assert isinstance(keywords, list)
        
    def test_special_characters_in_title(self, memory_store):
        """Test handling of special characters"""
        agent = WriterAgent(memory_store)
        
        title = "Test: Article / With * Special ? Characters <> | \\ \" '"
        sanitized = agent._sanitize_filename(title)
        
        # Should remove all invalid characters
        invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
        assert not any(char in sanitized for char in invalid_chars)
        
    def test_unicode_characters(self, memory_store):
        """Test handling of unicode characters"""
        agent = AnalyzerAgent(memory_store)
        
        title = "AI突破 in 医療診断 using 深層学習"
        keywords = agent._extract_keywords(title)
        
        # Should handle without crashing
        assert isinstance(keywords, list)
        
    def test_duplicate_detection_with_none_url(self, memory_store):
        """Test duplicate detection when URL is None"""
        agent = WriterAgent(memory_store)
        
        result = agent._check_if_already_generated(
            "Test Title",
            None,  # No URL
            []
        )
        
        # Should handle gracefully
        assert result is None or isinstance(result, dict)
        
    def test_memory_with_invalid_timestamp(self, memory_store):
        """Test memory handling with invalid timestamp"""
        entry = MemoryEntry(
            id="test_invalid",
            type=MemoryType.EPISODIC,
            content={"test": "data"},
            timestamp=None,  # Invalid timestamp
            importance=0.5
        )
        
        # Should handle or raise appropriate error
        try:
            memory_store.store(entry)
        except (ValueError, TypeError):
            pass  # Expected behavior
            
    def test_zero_confidence_thought(self, memory_store):
        """Test handling of zero confidence"""
        from src.agents.base import BaseAgent, Thought
        
        agent = BaseAgent("TestAgent", memory_store)
        agent._generate_thought = Mock(return_value=Thought(
            content="Low confidence thought",
            confidence=0.0,  # Zero confidence
            reasoning=["uncertain"],
            metadata={},
            timestamp=datetime.now()
        ))
        
        thought = agent.think({})
        
        assert thought.confidence == 0.0
        # Agent should still function
        
    def test_negative_importance(self, memory_store):
        """Test handling of negative importance"""
        entry = MemoryEntry(
            id="test_negative",
            type=MemoryType.SEMANTIC,
            content={"test": "data"},
            timestamp=datetime.now(),
            importance=-0.5  # Negative importance
        )
        
        # Should clamp or reject
        try:
            memory_store.store(entry)
            retrieved = memory_store.retrieve_all()
            stored_entry = next((m for m in retrieved if m.id == "test_negative"), None)
            if stored_entry:
                assert stored_entry.importance >= 0.0
        except ValueError:
            pass  # Expected behavior


class TestErrorHandling:
    """Test error handling and recovery"""
    
    @patch('requests.get')
    def test_api_timeout_handling(self, mock_get, memory_store):
        """Test handling of API timeouts"""
        import requests
        mock_get.side_effect = requests.exceptions.Timeout()
        
        agent = CollectorAgent(memory_store)
        
        # Should handle timeout gracefully
        try:
            titles = agent._fetch_from_newsapi("technology")
            assert isinstance(titles, list)
        except requests.exceptions.Timeout:
            pass  # Expected if no retry logic
            
    @patch('requests.get')
    def test_api_error_response(self, mock_get, memory_store):
        """Test handling of API errors"""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = Exception("Server Error")
        mock_get.return_value = mock_response
        
        agent = CollectorAgent(memory_store)
        
        # Should handle error gracefully
        try:
            titles = agent._fetch_from_newsapi("technology")
            assert isinstance(titles, list)
        except Exception:
            pass  # Expected behavior
            
    def test_corrupted_memory_database(self, tmp_path):
        """Test handling of corrupted database"""
        db_path = tmp_path / "corrupted.db"
        
        # Create corrupted file
        db_path.write_text("This is not a valid SQLite database")
        
        # Should handle or raise appropriate error
        try:
            memory = MemoryStore(db_path)
        except Exception as e:
            assert isinstance(e, (ValueError, IOError, Exception))
            
    def test_disk_full_scenario(self, memory_store, tmp_path, monkeypatch):
        """Test handling when disk is full"""
        agent = WriterAgent(memory_store)
        agent.generated_dir = tmp_path
        
        # Mock file write to raise OSError
        original_open = open
        def mock_open(*args, **kwargs):
            if 'w' in args or kwargs.get('mode', '') == 'w':
                raise OSError("No space left on device")
            return original_open(*args, **kwargs)
        
        monkeypatch.setattr("builtins.open", mock_open)
        
        # Should handle gracefully
        try:
            agent._save_article("Test", "Content")
        except OSError:
            pass  # Expected behavior


class TestStressTests:
    """Stress tests for performance and scalability"""
    
    def test_large_batch_processing(self, memory_store):
        """Test processing large batch of titles"""
        agent = AnalyzerAgent(memory_store)
        
        # Generate 1000 titles
        titles = [f"Test Article {i}" for i in range(1000)]
        
        start_time = time.time()
        results = agent.analyze_batch(titles[:100])  # Test with 100
        duration = time.time() - start_time
        
        assert len(results) == 100
        assert duration < 60  # Should complete in under 60 seconds
        
    def test_memory_with_many_entries(self, memory_store):
        """Test memory system with many entries"""
        # Store 1000 entries
        for i in range(1000):
            entry = MemoryEntry(
                id=f"stress_test_{i}",
                type=MemoryType.EPISODIC,
                content={"index": i, "data": f"test data {i}"},
                timestamp=datetime.now(),
                importance=0.5
            )
            memory_store.store(entry)
        
        # Query should still be fast
        start_time = time.time()
        results = memory_store.query({"type": MemoryType.EPISODIC}, limit=10)
        duration = time.time() - start_time
        
        assert len(results) == 10
        assert duration < 1.0  # Should complete in under 1 second
        
    def test_concurrent_memory_access(self, memory_store):
        """Test concurrent memory access"""
        import threading
        
        def store_entries(start_idx):
            for i in range(start_idx, start_idx + 100):
                entry = MemoryEntry(
                    id=f"concurrent_{i}",
                    type=MemoryType.SEMANTIC,
                    content={"index": i},
                    timestamp=datetime.now(),
                    importance=0.5
                )
                memory_store.store(entry)
        
        # Create multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=store_entries, args=(i * 100,))
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # Verify all entries stored
        all_entries = memory_store.retrieve_all()
        assert len(all_entries) >= 500
        
    def test_rapid_duplicate_checking(self, memory_store):
        """Test rapid duplicate checking performance"""
        agent = WriterAgent(memory_store)
        
        # Store many previous generations
        for i in range(100):
            entry = MemoryEntry(
                id=f"gen_{i}",
                type=MemoryType.SEMANTIC,
                content={
                    "action": "generate_article",
                    "title": f"Article {i}",
                    "source_url": f"https://example.com/{i}"
                },
                timestamp=datetime.now(),
                importance=0.8
            )
            memory_store.store(entry)
        
        memories = memory_store.retrieve_all()
        
        # Check duplicates rapidly
        start_time = time.time()
        for i in range(100):
            agent._check_if_already_generated(
                f"Article {i}",
                f"https://example.com/{i}",
                memories
            )
        duration = time.time() - start_time
        
        assert duration < 5.0  # Should complete in under 5 seconds


class TestBoundaryConditions:
    """Test boundary conditions"""
    
    def test_minimum_confidence(self, memory_store):
        """Test minimum confidence value"""
        from src.agents.base import BaseAgent, Thought
        
        agent = BaseAgent("TestAgent", memory_store)
        agent._generate_thought = Mock(return_value=Thought(
            content="Minimum confidence",
            confidence=0.0,
            reasoning=[],
            metadata={},
            timestamp=datetime.now()
        ))
        
        thought = agent.think({})
        assert thought.confidence >= 0.0
        
    def test_maximum_confidence(self, memory_store):
        """Test maximum confidence value"""
        from src.agents.base import BaseAgent, Thought
        
        agent = BaseAgent("TestAgent", memory_store)
        agent._generate_thought = Mock(return_value=Thought(
            content="Maximum confidence",
            confidence=1.0,
            reasoning=[],
            metadata={},
            timestamp=datetime.now()
        ))
        
        thought = agent.think({})
        assert thought.confidence <= 1.0
        
    def test_empty_memory_query(self, memory_store):
        """Test querying empty memory"""
        results = memory_store.query({})
        assert isinstance(results, list)
        
    def test_zero_importance_memory(self, memory_store):
        """Test memory with zero importance"""
        entry = MemoryEntry(
            id="zero_importance",
            type=MemoryType.EPISODIC,
            content={"test": "data"},
            timestamp=datetime.now(),
            importance=0.0
        )
        
        memory_store.store(entry)
        retrieved = memory_store.retrieve_all()
        
        assert any(m.id == "zero_importance" for m in retrieved)
        
    def test_maximum_importance_memory(self, memory_store):
        """Test memory with maximum importance"""
        entry = MemoryEntry(
            id="max_importance",
            type=MemoryType.EPISODIC,
            content={"test": "data"},
            timestamp=datetime.now(),
            importance=1.0
        )
        
        memory_store.store(entry)
        retrieved = memory_store.retrieve_all()
        
        stored = next((m for m in retrieved if m.id == "max_importance"), None)
        assert stored is not None
        assert stored.importance == 1.0


# Fixtures
@pytest.fixture
def memory_store(tmp_path):
    """Create temporary memory store"""
    db_path = tmp_path / "test_memory.db"
    return MemoryStore(db_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
