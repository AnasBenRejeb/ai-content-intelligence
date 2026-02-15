# 🏗️ Architecture Documentation

## System Overview

The Multi-Agent News Intelligence System implements a **metacognitive agentic architecture** where autonomous agents collaborate to collect, analyze, and retrieve news content while continuously learning and adapting.

## Core Principles

### 1. Metacognition
Agents possess the ability to think about their own thinking:
- **Self-monitoring**: Track performance metrics
- **Self-evaluation**: Assess confidence and success rates
- **Self-regulation**: Adjust strategies based on reflection

### 2. Self-Reference
Each agent maintains a self-model:
```python
self_model = {
    "strengths": ["keyword_extraction", "semantic_analysis"],
    "weaknesses": [],
    "learned_patterns": ["Successful pattern: ..."],
    "performance_metrics": {...}
}
```

### 3. Memory Architecture

Four-layer memory system:

```
┌─────────────────────────────────────┐
│         Working Memory              │  Short-term context
│  (Current thoughts, active tasks)   │
└─────────────────────────────────────┘
           ↓           ↑
┌─────────────────────────────────────┐
│        Episodic Memory              │  Specific experiences
│  (Past actions, reflections)        │
└─────────────────────────────────────┘
           ↓           ↑
┌─────────────────────────────────────┐
│        Semantic Memory              │  General knowledge
│  (Patterns, insights, facts)        │
└─────────────────────────────────────┘
           ↓           ↑
┌─────────────────────────────────────┐
│       Procedural Memory             │  How-to knowledge
│  (Skills, strategies, methods)      │
└─────────────────────────────────────┘
```

## Agent Architecture

### Base Agent Structure

```
BaseAgent
├── Cognitive Loop
│   ├── Think()      → Generate thoughts with reasoning
│   ├── Act()        → Execute planned actions
│   ├── Reflect()    → Metacognitive reflection
│   └── Learn()      → Extract and store patterns
│
├── Memory Interface
│   ├── Store()      → Persist experiences
│   ├── Retrieve()   → Access relevant memories
│   └── Query()      → Search memory by criteria
│
└── Self-Model
    ├── Strengths    → Known capabilities
    ├── Weaknesses   → Areas for improvement
    ├── Patterns     → Learned behaviors
    └── Metrics      → Performance tracking
```

### Specialized Agents

#### CollectorAgent
**Purpose**: Gather news titles from multiple sources

**Cognitive Process**:
1. **Think**: Analyze category and past performance
2. **Act**: Fetch titles via NewsAPI
3. **Reflect**: Evaluate collection efficiency
4. **Learn**: Optimize deduplication strategies

**Key Capabilities**:
- Multi-category collection
- Fuzzy deduplication
- Language detection
- Source cleaning

#### AnalyzerAgent
**Purpose**: Extract keywords and generate search queries

**Cognitive Process**:
1. **Think**: Consider title semantics
2. **Act**: Extract keywords using KeyBERT
3. **Reflect**: Assess keyword quality
4. **Learn**: Improve extraction patterns

**Key Capabilities**:
- Semantic keyword extraction
- Query optimization
- N-gram analysis
- Deduplication

#### RetrieverAgent
**Purpose**: Fetch full article content

**Cognitive Process**:
1. **Think**: Plan retrieval strategy
2. **Act**: Search and fetch articles
3. **Reflect**: Evaluate retrieval success
4. **Learn**: Optimize caching and search

**Key Capabilities**:
- Article search (GNews API)
- Content extraction
- Intelligent caching
- Retry logic

## Orchestrator

The orchestrator coordinates agent collaboration:

```
Orchestrator
├── Agent Management
│   ├── Initialize agents
│   ├── Coordinate execution
│   └── Monitor performance
│
├── Pipeline Execution
│   ├── Phase 1: Collection
│   ├── Phase 2: Analysis
│   └── Phase 3: Retrieval
│
├── Metacognitive Oversight
│   ├── System-level reflection
│   ├── Cross-agent insights
│   └── Performance optimization
│
└── Reporting
    ├── Agent statuses
    ├── Performance metrics
    └── Execution history
```

## Data Flow

```
┌──────────────┐
│  NewsAPI     │
└──────┬───────┘
       │ titles
       ↓
┌──────────────────┐
│ CollectorAgent   │ → Deduplicate → Store in Memory
└──────┬───────────┘
       │ unique titles
       ↓
┌──────────────────┐
│ AnalyzerAgent    │ → Extract Keywords → Store in Memory
└──────┬───────────┘
       │ queries
       ↓
┌──────────────────┐
│ RetrieverAgent   │ → Fetch Articles → Cache & Store
└──────┬───────────┘
       │ articles
       ↓
┌──────────────────┐
│  Article Store   │
└──────────────────┘
```

## Metacognitive Loop

Each agent follows this continuous loop:

```
     ┌─────────────┐
     │   THINK     │ ← Generate thought with reasoning
     └──────┬──────┘
            │
            ↓
     ┌─────────────┐
     │    ACT      │ ← Execute planned action
     └──────┬──────┘
            │
            ↓
     ┌─────────────┐
     │  REFLECT    │ ← Observe & generate insights
     └──────┬──────┘
            │
            ↓
     ┌─────────────┐
     │   LEARN     │ ← Extract patterns & update model
     └──────┬──────┘
            │
            └──────→ (back to THINK)
```

## Memory Persistence

SQLite-based persistent storage:

```sql
CREATE TABLE memories (
    id TEXT PRIMARY KEY,
    type TEXT NOT NULL,           -- episodic, semantic, etc.
    content TEXT NOT NULL,        -- JSON-encoded content
    timestamp TEXT NOT NULL,
    importance REAL NOT NULL,     -- 0.0 to 1.0
    access_count INTEGER,
    last_accessed TEXT,
    metadata TEXT
);
```

## Performance Optimization

### Caching Strategy
- Article content cached locally
- Memory queries optimized with indexes
- Batch processing for efficiency

### Retry Logic
- Exponential backoff for API calls
- Configurable retry attempts
- Graceful degradation

### Parallel Processing
- Configurable worker threads
- Async-ready architecture
- Non-blocking operations

## Extensibility

### Adding New Agents

```python
from src.agents.base import BaseAgent

class CustomAgent(BaseAgent):
    def __init__(self, memory_store):
        super().__init__("CustomAgent", memory_store)
        self.self_model["strengths"] = ["custom_capability"]
    
    def _generate_thought(self, context, memories):
        # Custom thinking logic
        return Thought(...)
    
    def _plan_action(self, thought):
        # Custom planning logic
        return Action(...)
    
    def _execute_action(self, action):
        # Custom execution logic
        return {...}
```

### Custom Memory Types

```python
class MemoryType(Enum):
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    PROCEDURAL = "procedural"
    WORKING = "working"
    CUSTOM = "custom"  # Add your type
```

## Configuration

All system parameters configurable via `config.py`:

```python
class Settings(BaseSettings):
    # API keys
    newsapi_key: str
    gnews_api_key: str
    
    # Agent parameters
    categories: List[str]
    page_size: int
    similarity_threshold: int
    
    # Metacognitive parameters
    reflection_interval: int
    confidence_threshold: float
    learning_rate: float
```

## Error Handling

Multi-level error handling:

1. **Agent Level**: Try-catch in action execution
2. **Orchestrator Level**: Pipeline error recovery
3. **System Level**: Graceful degradation

## Monitoring & Observability

Built-in monitoring:
- Agent state tracking
- Performance metrics
- Execution history
- Memory statistics
- Reflection insights

## Future Enhancements

Potential improvements:

1. **Vector Memory**: Semantic similarity search
2. **Multi-Modal**: Image and video processing
3. **Distributed**: Multi-machine coordination
4. **Advanced NLP**: Transformer-based models
5. **Real-Time**: Streaming data processing
6. **Collaborative**: Inter-agent communication protocols

---

This architecture enables autonomous, adaptive, and intelligent news processing with continuous learning and improvement.
