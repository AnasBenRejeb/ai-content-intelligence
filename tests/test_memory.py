"""Tests for memory system"""
import pytest
from datetime import datetime
from src.memory.base import MemoryStore, MemoryEntry, MemoryType


@pytest.fixture
def memory_store(tmp_path):
    """Create temporary memory store"""
    return MemoryStore(tmp_path / "test_memory.db")


def test_store_and_retrieve(memory_store):
    """Test storing and retrieving memory"""
    entry = MemoryEntry(
        id="test_1",
        type=MemoryType.EPISODIC,
        content={"test": "data"},
        timestamp=datetime.now(),
        importance=0.8
    )
    
    memory_store.store(entry)
    retrieved = memory_store.retrieve("test_1")
    
    assert retrieved is not None
    assert retrieved.id == "test_1"
    assert retrieved.content["test"] == "data"


def test_query_by_type(memory_store):
    """Test querying by memory type"""
    # Store different types
    for i, mem_type in enumerate([MemoryType.EPISODIC, MemoryType.SEMANTIC]):
        entry = MemoryEntry(
            id=f"test_{i}",
            type=mem_type,
            content={"index": i},
            timestamp=datetime.now(),
            importance=0.5
        )
        memory_store.store(entry)
    
    # Query episodic
    results = memory_store.query(memory_type=MemoryType.EPISODIC)
    assert len(results) == 1
    assert results[0].type == MemoryType.EPISODIC


def test_query_by_importance(memory_store):
    """Test querying by importance"""
    # Store with different importance
    for i in range(3):
        entry = MemoryEntry(
            id=f"test_{i}",
            type=MemoryType.SEMANTIC,
            content={"index": i},
            timestamp=datetime.now(),
            importance=i * 0.3
        )
        memory_store.store(entry)
    
    # Query high importance
    results = memory_store.query(min_importance=0.5)
    assert len(results) == 1
    assert results[0].importance >= 0.5
