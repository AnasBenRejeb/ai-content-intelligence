"""Tests for orchestrator"""
import pytest
from src.orchestrator import Orchestrator


def test_orchestrator_initialization():
    """Test orchestrator initialization"""
    orch = Orchestrator()
    
    assert orch.collector is not None
    assert orch.analyzer is not None
    assert orch.retriever is not None
    assert len(orch.agents) == 3


def test_get_agent_statuses():
    """Test getting agent statuses"""
    orch = Orchestrator()
    statuses = orch.get_agent_statuses()
    
    assert "CollectorAgent" in statuses
    assert "AnalyzerAgent" in statuses
    assert "RetrieverAgent" in statuses


def test_system_report():
    """Test system report generation"""
    orch = Orchestrator()
    report = orch.get_system_report()
    
    assert "MULTI-AGENT NEWS INTELLIGENCE SYSTEM" in report
    assert "PERFORMANCE METRICS" in report
    assert "AGENT STATUSES" in report
