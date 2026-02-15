"""Base agent with metacognitive capabilities"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, field
import uuid
from enum import Enum

from ..memory.base import MemoryStore, MemoryEntry, MemoryType


class AgentState(Enum):
    """Agent operational states"""
    IDLE = "idle"
    THINKING = "thinking"
    ACTING = "acting"
    REFLECTING = "reflecting"
    LEARNING = "learning"


@dataclass
class Thought:
    """Represents an agent's thought"""
    content: str
    confidence: float
    reasoning: List[str]
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Action:
    """Represents an agent action"""
    name: str
    parameters: Dict[str, Any]
    expected_outcome: str
    confidence: float
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class Reflection:
    """Metacognitive reflection"""
    trigger: str
    observations: List[str]
    insights: List[str]
    adjustments: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)


class BaseAgent(ABC):
    """Base agent with metacognitive capabilities"""
    
    def __init__(self, name: str, memory_store: MemoryStore):
        self.name = name
        self.id = str(uuid.uuid4())
        self.memory = memory_store
        self.state = AgentState.IDLE
        
        # Metacognitive components
        self.thoughts: List[Thought] = []
        self.actions_taken: List[Action] = []
        self.reflections: List[Reflection] = []
        
        # Performance tracking
        self.success_count = 0
        self.failure_count = 0
        self.confidence_history: List[float] = []
        
        # Self-reference
        self.self_model = {
            "strengths": [],
            "weaknesses": [],
            "learned_patterns": [],
            "performance_metrics": {}
        }
    
    def think(self, context: Dict[str, Any]) -> Thought:
        """Generate a thought based on context"""
        self.state = AgentState.THINKING
        
        # Retrieve relevant memories
        relevant_memories = self._retrieve_relevant_memories(context)
        
        # Generate thought with reasoning
        thought = self._generate_thought(context, relevant_memories)
        self.thoughts.append(thought)
        
        # Store thought in episodic memory
        self._store_thought(thought)
        
        return thought
    
    def act(self, thought: Thought) -> Dict[str, Any]:
        """Execute action based on thought"""
        self.state = AgentState.ACTING
        
        # Plan action
        action = self._plan_action(thought)
        self.actions_taken.append(action)
        
        # Execute
        result = self._execute_action(action)
        
        # Update performance
        self._update_performance(action, result)
        
        return result
    
    def reflect(self, trigger: str = "periodic") -> Reflection:
        """Metacognitive reflection on recent performance"""
        self.state = AgentState.REFLECTING
        
        observations = self._observe_recent_performance()
        insights = self._generate_insights(observations)
        adjustments = self._plan_adjustments(insights)
        
        reflection = Reflection(
            trigger=trigger,
            observations=observations,
            insights=insights,
            adjustments=adjustments
        )
        
        self.reflections.append(reflection)
        self._store_reflection(reflection)
        self._apply_adjustments(adjustments)
        
        return reflection
    
    def learn(self, experience: Dict[str, Any]):
        """Learn from experience"""
        self.state = AgentState.LEARNING
        
        # Extract patterns
        patterns = self._extract_patterns(experience)
        
        # Update self-model
        self._update_self_model(patterns)
        
        # Store in semantic memory
        memory_entry = MemoryEntry(
            id=str(uuid.uuid4()),
            type=MemoryType.SEMANTIC,
            content={"patterns": patterns, "experience": experience},
            timestamp=datetime.now(),
            importance=self._calculate_importance(experience)
        )
        self.memory.store(memory_entry)
    
    @abstractmethod
    def _generate_thought(self, context: Dict[str, Any], 
                         memories: List[MemoryEntry]) -> Thought:
        """Generate thought - to be implemented by subclasses"""
        pass
    
    @abstractmethod
    def _plan_action(self, thought: Thought) -> Action:
        """Plan action - to be implemented by subclasses"""
        pass
    
    @abstractmethod
    def _execute_action(self, action: Action) -> Dict[str, Any]:
        """Execute action - to be implemented by subclasses"""
        pass
    
    def _retrieve_relevant_memories(self, context: Dict[str, Any]) -> List[MemoryEntry]:
        """Retrieve relevant memories for context"""
        # Simple retrieval - can be enhanced with vector similarity
        return self.memory.query(limit=5, min_importance=0.5)
    
    def _observe_recent_performance(self) -> List[str]:
        """Observe recent performance"""
        observations = []
        
        if len(self.actions_taken) > 0:
            recent_actions = self.actions_taken[-10:]
            avg_confidence = sum(a.confidence for a in recent_actions) / len(recent_actions)
            observations.append(f"Average confidence in last 10 actions: {avg_confidence:.2f}")
        
        if self.success_count + self.failure_count > 0:
            success_rate = self.success_count / (self.success_count + self.failure_count)
            observations.append(f"Success rate: {success_rate:.2%}")
        
        return observations
    
    def _generate_insights(self, observations: List[str]) -> List[str]:
        """Generate insights from observations"""
        insights = []
        
        for obs in observations:
            if "confidence" in obs.lower() and "0.5" in obs:
                insights.append("Confidence levels are moderate - may need more training data")
            elif "success rate" in obs.lower():
                if "0.8" in obs or "0.9" in obs:
                    insights.append("High success rate indicates good performance")
                elif "0.3" in obs or "0.4" in obs:
                    insights.append("Low success rate - strategy adjustment needed")
        
        return insights
    
    def _plan_adjustments(self, insights: List[str]) -> Dict[str, Any]:
        """Plan adjustments based on insights"""
        adjustments = {}
        
        for insight in insights:
            if "training data" in insight.lower():
                adjustments["increase_memory_retrieval"] = True
            elif "strategy adjustment" in insight.lower():
                adjustments["revise_action_planning"] = True
        
        return adjustments
    
    def _apply_adjustments(self, adjustments: Dict[str, Any]):
        """Apply adjustments to agent behavior"""
        for key, value in adjustments.items():
            if key in self.self_model:
                self.self_model[key] = value
    
    def _extract_patterns(self, experience: Dict[str, Any]) -> List[str]:
        """Extract patterns from experience"""
        patterns = []
        
        if "success" in experience and experience["success"]:
            patterns.append(f"Successful pattern: {experience.get('action', 'unknown')}")
        
        return patterns
    
    def _update_self_model(self, patterns: List[str]):
        """Update self-model with learned patterns"""
        self.self_model["learned_patterns"].extend(patterns)
        
        # Keep only recent patterns
        if len(self.self_model["learned_patterns"]) > 100:
            self.self_model["learned_patterns"] = self.self_model["learned_patterns"][-100:]
    
    def _update_performance(self, action: Action, result: Dict[str, Any]):
        """Update performance metrics"""
        if result.get("success", False):
            self.success_count += 1
        else:
            self.failure_count += 1
        
        self.confidence_history.append(action.confidence)
    
    def _calculate_importance(self, experience: Dict[str, Any]) -> float:
        """Calculate importance of experience"""
        importance = 0.5
        
        if experience.get("success"):
            importance += 0.3
        if experience.get("novel"):
            importance += 0.2
        
        return min(importance, 1.0)
    
    def _store_thought(self, thought: Thought):
        """Store thought in memory"""
        memory_entry = MemoryEntry(
            id=str(uuid.uuid4()),
            type=MemoryType.WORKING,
            content={"thought": thought.content, "confidence": thought.confidence},
            timestamp=thought.timestamp,
            importance=thought.confidence
        )
        self.memory.store(memory_entry)
    
    def _store_reflection(self, reflection: Reflection):
        """Store reflection in memory"""
        memory_entry = MemoryEntry(
            id=str(uuid.uuid4()),
            type=MemoryType.EPISODIC,
            content={
                "trigger": reflection.trigger,
                "insights": reflection.insights,
                "adjustments": reflection.adjustments
            },
            timestamp=reflection.timestamp,
            importance=0.8
        )
        self.memory.store(memory_entry)
    
    def get_status(self) -> Dict[str, Any]:
        """Get agent status"""
        return {
            "name": self.name,
            "id": self.id,
            "state": self.state.value,
            "thoughts_count": len(self.thoughts),
            "actions_count": len(self.actions_taken),
            "reflections_count": len(self.reflections),
            "success_rate": self.success_count / max(1, self.success_count + self.failure_count),
            "self_model": self.self_model
        }
