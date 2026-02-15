# 🎓 Engineer Onboarding Guide

## Welcome to the Team!

This guide will help you understand our Multi-Agent News Intelligence System from the ground up.

---

## Table of Contents

1. [Design Patterns We Use](#design-patterns-we-use)
2. [System Architecture Deep Dive](#system-architecture-deep-dive)
3. [Code Walkthrough](#code-walkthrough)
4. [Key Concepts](#key-concepts)
5. [Development Workflow](#development-workflow)
6. [Common Tasks](#common-tasks)
7. [Debugging Guide](#debugging-guide)
8. [Best Practices](#best-practices)

---

## Design Patterns We Use

### 1. Metacognitive Pattern (Core Innovation)

**What it is**: Agents that think about their own thinking

**Why we use it**: Enables self-improvement and learning

**How it works**:
```python
# Traditional approach (no learning)
def process_article(article):
    return analyze(article)

# Our metacognitive approach (learns and improves)
class Agent:
    def process_article(self, article):
        # THINK: Should I process this? How?
        thought = self.think(article)
        
        # ACT: Execute based on thought
        result = self.act(thought)
        
        # REFLECT: How did I do?
        self.reflect(result)
        
        # LEARN: Store for future
        self.learn(result)
        
        return result
```

**Real example in our code**:
```python
# src/agents/base.py
class BaseAgent:
    def think(self, context: Dict) -> Thought:
        """Generate thought about situation"""
        # Retrieve relevant memories
        memories = self.memory.query(context)
        
        # Generate reasoning
        thought = self._generate_thought(context, memories)
        
        # Store thought for reflection
        self.thoughts.append(thought)
        
        return thought
```

**Benefits**:
- Agents improve over time
- Learn from mistakes
- Adapt to patterns
- Self-aware of performance

### 2. Agent Pattern

**What it is**: Autonomous entities with specific responsibilities

**Why we use it**: Separation of concerns, scalability

**Our agents**:
```
CollectorAgent  → Collects news titles
AnalyzerAgent   → Extracts keywords
RetrieverAgent  → Fetches full articles
WriterAgent     → Generates new content
```

**Key characteristics**:
- **Autonomous**: Each agent makes its own decisions
- **Specialized**: Each has specific strengths
- **Communicative**: Share data through orchestrator
- **Self-aware**: Track their own performance

**Example**:
```python
class CollectorAgent(BaseAgent):
    def __init__(self, memory_store):
        super().__init__("CollectorAgent", memory_store)
        # Define strengths
        self.self_model["strengths"] = ["news_collection", "deduplication"]
        
    def _generate_thought(self, context, memories):
        # Agent decides: Should I collect from this category?
        category = context.get("category")
        
        # Check past performance
        past_success = self._check_past_success(category, memories)
        
        # Make decision
        confidence = 0.5 + (past_success * 0.4)
        
        return Thought(
            content=f"Collect from {category}",
            confidence=confidence,
            reasoning=[f"Past success: {past_success:.1%}"]
        )
```

### 3. Strategy Pattern

**What it is**: Select algorithm at runtime based on context

**Why we use it**: Flexibility and adaptability

**Example in our code**:
```python
class WriterAgent:
    def _execute_action(self, action):
        # Strategy 1: Use LLM if available
        if self.llm and action.parameters["use_llm"]:
            return self._generate_with_llm(title, content)
        
        # Strategy 2: Use template as fallback
        else:
            return self._generate_template(title)
```

**Benefits**:
- Graceful degradation
- Multiple approaches
- Easy to add new strategies

### 4. Observer Pattern

**What it is**: Objects observe and react to events

**Why we use it**: Agents learn from outcomes

**Example**:
```python
class BaseAgent:
    def act(self, thought):
        # Execute action
        result = self._execute_action(action)
        
        # Observe outcome
        if result.get("success"):
            self.success_count += 1
            self.learn({"action": action.name, "success": True})
        else:
            self.failure_count += 1
            self.learn({"action": action.name, "success": False})
```

### 5. Memento Pattern

**What it is**: Capture and restore object state

**Why we use it**: Persistent memory across runs

**Example**:
```python
class MemoryStore:
    def store(self, entry: MemoryEntry):
        """Save state to database"""
        # State is preserved even after restart
        
    def retrieve(self, query: str):
        """Restore previous state"""
        # Agent can access past experiences
```

### 6. Chain of Responsibility

**What it is**: Pass request through chain of handlers

**Why we use it**: Pipeline processing

**Our pipeline**:
```
Input → Collector → Analyzer → Retriever → Writer → Output
         ↓           ↓           ↓           ↓
      Memory      Memory      Memory      Memory
```

**Example**:
```python
class Orchestrator:
    def run_pipeline(self):
        # Phase 1: Collection
        collected = self.collector.collect_all_categories()
        
        # Phase 2: Analysis (uses Phase 1 output)
        analyzed = self.analyzer.analyze_batch(collected)
        
        # Phase 3: Retrieval (uses Phase 2 output)
        retrieved = self.retriever.retrieve_batch(analyzed)
        
        # Phase 4: Generation (uses Phase 3 output)
        generated = self.writer.generate_batch(retrieved)
```

### 7. Template Method Pattern

**What it is**: Define skeleton, let subclasses fill in steps

**Why we use it**: Consistent agent behavior

**Example**:
```python
class BaseAgent:
    # Template method (same for all agents)
    def think(self, context):
        memories = self.memory.query(context)
        thought = self._generate_thought(context, memories)  # Subclass implements
        self.thoughts.append(thought)
        return thought
    
    # Abstract method (each agent implements differently)
    def _generate_thought(self, context, memories):
        raise NotImplementedError
```

---

## System Architecture Deep Dive

### High-Level View

```
┌─────────────────────────────────────────────────────────┐
│                    USER/SCHEDULER                       │
│                    (Triggers execution)                 │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                   ORCHESTRATOR                          │
│  - Coordinates all agents                               │
│  - Manages pipeline flow                                │
│  - Tracks system metrics                                │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┼────────────┬────────────┐
        │            │            │            │
        ▼            ▼            ▼            ▼
┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
│Collector │  │Analyzer  │  │Retriever │  │ Writer   │
│  Agent   │  │  Agent   │  │  Agent   │  │  Agent   │
└────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘
     │             │             │             │
     └─────────────┴─────────────┴─────────────┘
                   │
                   ▼
         ┌─────────────────┐
         │  SHARED MEMORY  │
         │   (SQLite DB)   │
         └─────────────────┘
```

### Component Interaction

**Scenario**: Generate article about "AI in Healthcare"

```
1. USER triggers execution
   ↓
2. ORCHESTRATOR starts pipeline
   ↓
3. COLLECTOR thinks: "Should I collect from 'technology'?"
   - Checks memory: Last success rate 92%
   - Decision: Yes, confidence 0.85
   - Acts: Calls NewsAPI
   - Result: 50 titles collected
   - Reflects: "Good success rate, store in memory"
   ↓
4. ANALYZER thinks: "Should I analyze 'AI in Healthcare'?"
   - Checks memory: Similar titles analyzed before
   - Decision: Yes, confidence 0.80
   - Acts: Extracts keywords ["AI", "healthcare", "medical"]
   - Result: 5 keywords extracted
   - Reflects: "Good keyword quality"
   ↓
5. RETRIEVER thinks: "Should I retrieve this article?"
   - Checks cache: Not found
   - Checks memory: 85% success rate
   - Decision: Yes, confidence 0.75
   - Acts: Searches GNews, fetches content
   - Result: Article retrieved (2500 chars)
   - Reflects: "Good content quality"
   ↓
6. WRITER thinks: "Should I generate article?"
   - Checks duplicates:
     * Title similarity: No match
     * URL check: Not generated before
     * File check: Doesn't exist
   - Decision: Yes, confidence 0.85
   - Acts: Generates with LLM (487 words)
   - Result: Article generated
   - Reflects: "Good generation quality"
   ↓
7. ORCHESTRATOR collects results
   - Updates metrics
   - Triggers agent reflections
   - Stores execution in memory
```

### Data Structures

**Thought** (Agent's reasoning):
```python
@dataclass
class Thought:
    content: str              # "Should I collect from technology?"
    confidence: float         # 0.85 (0.0 to 1.0)
    reasoning: List[str]      # ["Past success: 92%", "Rate limits OK"]
    metadata: Dict[str, Any]  # {"category": "technology"}
    timestamp: datetime       # When thought occurred
```

**Action** (Agent's decision):
```python
@dataclass
class Action:
    name: str                 # "collect_titles"
    parameters: Dict          # {"category": "technology", "pages": 3}
    expected_outcome: str     # "Collect 10-50 titles"
    confidence: float         # 0.85
    timestamp: datetime
```

**Memory Entry** (Stored experience):
```python
@dataclass
class MemoryEntry:
    id: str                   # "collection_tech_20250215"
    type: MemoryType          # EPISODIC, SEMANTIC, PROCEDURAL, WORKING
    content: Dict[str, Any]   # {"action": "collect", "success": True}
    timestamp: datetime
    importance: float         # 0.8 (higher = more important)
    access_count: int         # How many times accessed
    last_accessed: datetime
```

---


## Code Walkthrough

### Starting Point: run.py

```python
# run.py - Entry point
from src.main import main

if __name__ == "__main__":
    main()  # Starts the system
```

### Main Execution: src/main.py

```python
def main():
    # 1. Load configuration
    settings = load_config()
    
    # 2. Initialize orchestrator
    orchestrator = Orchestrator()
    
    # 3. Run pipeline
    result = orchestrator.run_pipeline()
    
    # 4. Display results
    print(orchestrator.get_system_report())
```

### Orchestrator: src/orchestrator.py

```python
class Orchestrator:
    def __init__(self):
        # Shared memory for all agents
        self.shared_memory = MemoryStore("memory_store/shared_memory.db")
        
        # Initialize all agents with shared memory
        self.collector = CollectorAgent(self.shared_memory)
        self.analyzer = AnalyzerAgent(self.shared_memory)
        self.retriever = RetrieverAgent(self.shared_memory)
        self.writer = WriterAgent(self.shared_memory)
    
    def run_pipeline(self):
        # Phase 1: Collect
        collected = self.collector.collect_all_categories()
        
        # Phase 2: Analyze
        analyzed = self.analyzer.analyze_batch(collected)
        
        # Phase 3: Retrieve
        retrieved = self.retriever.retrieve_batch(analyzed)
        
        # Phase 4: Generate
        generated = self.writer.generate_batch(retrieved)
        
        return {"collected": collected, "generated": generated}
```

### Base Agent: src/agents/base.py

```python
class BaseAgent:
    def __init__(self, name, memory_store):
        self.name = name
        self.memory = memory_store
        self.thoughts = []
        self.actions_taken = []
        self.success_count = 0
        self.failure_count = 0
        self.self_model = {
            "strengths": [],
            "weaknesses": [],
            "learned_patterns": []
        }
    
    # THINK phase
    def think(self, context: Dict) -> Thought:
        # 1. Retrieve relevant memories
        memories = self.memory.query(context)
        
        # 2. Generate thought (subclass implements)
        thought = self._generate_thought(context, memories)
        
        # 3. Store thought
        self.thoughts.append(thought)
        
        return thought
    
    # ACT phase
    def act(self, thought: Thought) -> Dict:
        # 1. Plan action
        action = self._plan_action(thought)
        
        # 2. Execute action
        result = self._execute_action(action)
        
        # 3. Record action
        self.actions_taken.append(action)
        
        # 4. Update metrics
        if result.get("success"):
            self.success_count += 1
        else:
            self.failure_count += 1
        
        return result
    
    # REFLECT phase
    def reflect(self, trigger: str) -> Reflection:
        # 1. Analyze recent performance
        recent_actions = self.actions_taken[-10:]
        success_rate = self.success_count / max(1, len(self.actions_taken))
        
        # 2. Generate insights
        insights = [
            f"Success rate: {success_rate:.1%}",
            f"Total actions: {len(self.actions_taken)}",
            f"Recent trend: {'improving' if success_rate > 0.7 else 'needs work'}"
        ]
        
        # 3. Create reflection
        reflection = Reflection(
            trigger=trigger,
            insights=insights,
            performance_summary={"success_rate": success_rate}
        )
        
        # 4. Store reflection
        self.reflections.append(reflection)
        
        return reflection
    
    # LEARN phase
    def learn(self, outcome: Dict):
        # Store in memory for future use
        memory_entry = MemoryEntry(
            id=f"{self.name}_{datetime.now().timestamp()}",
            type=MemoryType.SEMANTIC,
            content=outcome,
            timestamp=datetime.now(),
            importance=0.7
        )
        self.memory.store(memory_entry)
```

### Example Agent: src/agents/collector.py

```python
class CollectorAgent(BaseAgent):
    def __init__(self, memory_store):
        super().__init__("CollectorAgent", memory_store)
        self.newsapi_key = settings.newsapi_key
        self.self_model["strengths"] = ["news_collection", "deduplication"]
    
    def _generate_thought(self, context, memories):
        """Decide if we should collect from this category"""
        category = context.get("category")
        
        # Check past performance
        past_success = sum(
            1 for m in memories 
            if m.content.get("category") == category 
            and m.content.get("success")
        ) / max(1, len(memories))
        
        # Calculate confidence
        confidence = 0.5 + (past_success * 0.4)
        
        return Thought(
            content=f"Collect from {category}",
            confidence=confidence,
            reasoning=[
                f"Category: {category}",
                f"Past success: {past_success:.1%}",
                f"Confidence: {confidence:.1%}"
            ],
            metadata={"category": category}
        )
    
    def _plan_action(self, thought):
        """Plan collection action"""
        return Action(
            name="collect_titles",
            parameters={
                "category": thought.metadata["category"],
                "pages": settings.pages_per_category
            },
            expected_outcome="Collect 10-50 titles",
            confidence=thought.confidence
        )
    
    def _execute_action(self, action):
        """Execute collection"""
        try:
            # Call NewsAPI
            titles = self._fetch_from_newsapi(action.parameters["category"])
            
            # Deduplicate
            unique_titles = self._deduplicate_titles(titles)
            
            return {
                "success": True,
                "category": action.parameters["category"],
                "titles": unique_titles,
                "count": len(unique_titles)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
```

---

## Key Concepts

### 1. Metacognition

**Definition**: Thinking about thinking

**In our system**:
- Agents evaluate their own performance
- Learn from past experiences
- Adjust strategies based on outcomes
- Self-aware of strengths and weaknesses

**Example**:
```python
# Agent reflects on its performance
reflection = agent.reflect("periodic")

# Insights generated:
# - "Success rate improved from 75% to 85%"
# - "Technology category performs best"
# - "Should increase cache TTL for better performance"

# Agent updates its strategy based on insights
agent.self_model["learned_patterns"].append({
    "pattern": "technology_high_success",
    "action": "prioritize_technology_category"
})
```

### 2. Memory Layers

**4-Layer Architecture**:

1. **Working Memory** (Current context)
   - Active thoughts
   - Current action parameters
   - Immediate data

2. **Episodic Memory** (Specific events)
   - "Collected 50 titles at 10:30 AM"
   - "Generated article about AI in healthcare"
   - Timestamped, specific occurrences

3. **Semantic Memory** (General knowledge)
   - "Technology category has 90% success rate"
   - "Articles with 'AI' keyword get high engagement"
   - Patterns and generalizations

4. **Procedural Memory** (How-to knowledge)
   - "Retry on timeout works 85% of the time"
   - "Use LLM for articles > 500 words"
   - Strategies and procedures

**Why 4 layers?**
- Mimics human memory
- Different retrieval strategies
- Importance-based storage
- Efficient querying

### 3. Confidence Scoring

**How it works**:
```python
def calculate_confidence(self, context, memories):
    base_confidence = 0.5  # Start at 50%
    
    # Factor 1: Past success rate (+40%)
    past_success = self._get_past_success(memories)
    base_confidence += past_success * 0.4
    
    # Factor 2: Data quality (+10%)
    if self._has_good_data(context):
        base_confidence += 0.1
    
    # Factor 3: Resource availability (+5%)
    if self._resources_available():
        base_confidence += 0.05
    
    # Clamp to [0, 1]
    return min(max(base_confidence, 0.0), 1.0)
```

**Usage**:
- High confidence (>0.8): Proceed with action
- Medium confidence (0.5-0.8): Proceed with caution
- Low confidence (<0.5): Consider alternative strategy

### 4. Duplicate Detection

**3-Level System**:

**Level 1: Title Similarity (Fuzzy Matching)**
```python
from rapidfuzz import fuzz

def titles_similar(title1, title2, threshold=85):
    # Token sort ratio: Handles word order differences
    similarity = fuzz.token_sort_ratio(title1, title2)
    return similarity >= threshold

# Example:
# "AI Breakthrough in Medicine" vs "Medicine AI Breakthrough"
# Similarity: 100% → Duplicate!
```

**Level 2: URL Tracking**
```python
def check_url_duplicate(url, memories):
    for memory in memories:
        if memory.content.get("source_url") == url:
            return True  # Already generated from this URL
    return False
```

**Level 3: File Existence**
```python
def check_file_exists(title):
    filename = sanitize_filename(title)
    filepath = generated_dir / f"{filename}.md"
    return filepath.exists()
```

**Why 3 levels?**
- Catches different types of duplicates
- Redundancy ensures nothing slips through
- Each level is fast (<1ms)

---

## Development Workflow

### 1. Setting Up Development Environment

```bash
# Clone repository
git clone <repo-url>
cd news-intelligence-agents

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install in development mode
pip install -e .

# Install development dependencies
pip install pytest pytest-cov black flake8

# Verify installation
python -c "from src.orchestrator import Orchestrator; print('✅ Setup complete!')"
```

### 2. Making Changes

**Step 1: Create feature branch**
```bash
git checkout -b feature/your-feature-name
```

**Step 2: Make changes**
```python
# Example: Adding new agent
class CustomAgent(BaseAgent):
    def __init__(self, memory_store):
        super().__init__("CustomAgent", memory_store)
        self.self_model["strengths"] = ["custom_task"]
    
    def _generate_thought(self, context, memories):
        # Your logic here
        pass
```

**Step 3: Write tests**
```python
# tests/test_custom_agent.py
def test_custom_agent_initialization(memory_store):
    agent = CustomAgent(memory_store)
    assert agent.name == "CustomAgent"
    assert "custom_task" in agent.self_model["strengths"]
```

**Step 4: Run tests**
```bash
pytest tests/test_custom_agent.py -v
```

**Step 5: Format code**
```bash
black src/ tests/
flake8 src/ tests/
```

**Step 6: Commit**
```bash
git add .
git commit -m "feat: Add CustomAgent for X functionality"
```

### 3. Testing Strategy

**Unit Tests** (Test individual components):
```python
def test_agent_think():
    agent = BaseAgent("Test", memory_store)
    thought = agent.think({"test": "context"})
    assert thought.confidence >= 0.0
    assert thought.confidence <= 1.0
```

**Integration Tests** (Test component interaction):
```python
def test_pipeline_flow():
    orch = Orchestrator()
    result = orch.run_pipeline()
    assert result["success"]
```

**Edge Case Tests** (Test error scenarios):
```python
def test_empty_title_handling():
    agent = CollectorAgent(memory_store)
    titles = agent._deduplicate_titles(["", "Valid"])
    assert "" not in titles
```

### 4. Debugging

**Enable debug logging**:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

**Add breakpoints**:
```python
def _generate_thought(self, context, memories):
    import pdb; pdb.set_trace()  # Debugger stops here
    # Your code
```

**Check agent state**:
```python
agent = CollectorAgent(memory_store)
print(agent.get_status())
# Shows: success_rate, thoughts_count, actions_count, etc.
```

---

## Common Tasks

### Task 1: Add New Agent

```python
# 1. Create agent file
# src/agents/my_agent.py

from .base import BaseAgent, Thought, Action

class MyAgent(BaseAgent):
    def __init__(self, memory_store):
        super().__init__("MyAgent", memory_store)
        self.self_model["strengths"] = ["my_task"]
    
    def _generate_thought(self, context, memories):
        return Thought(
            content="My thought",
            confidence=0.8,
            reasoning=["reason1"],
            metadata={}
        )
    
    def _plan_action(self, thought):
        return Action(
            name="my_action",
            parameters={},
            expected_outcome="success",
            confidence=thought.confidence
        )
    
    def _execute_action(self, action):
        # Your logic
        return {"success": True}

# 2. Add to orchestrator
# src/orchestrator.py

self.my_agent = MyAgent(self.shared_memory)
self.agents.append(self.my_agent)

# 3. Add to pipeline
result = self.my_agent.process(data)
```

### Task 2: Modify Duplicate Detection

```python
# src/agents/writer.py

def _check_if_already_generated(self, title, url, memories):
    # Add new check: Content similarity
    for memory in memories:
        if memory.type == MemoryType.SEMANTIC:
            # Existing checks...
            
            # NEW: Check content similarity
            stored_content = memory.content.get("content_preview", "")
            if self._content_similar(content, stored_content):
                return {"reason": "similar_content"}
    
    return None

def _content_similar(self, content1, content2, threshold=90):
    """New method for content similarity"""
    from rapidfuzz import fuzz
    return fuzz.ratio(content1[:500], content2[:500]) >= threshold
```

### Task 3: Add New Memory Type

```python
# src/memory/base.py

class MemoryType(Enum):
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    PROCEDURAL = "procedural"
    WORKING = "working"
    CUSTOM = "custom"  # NEW

# Use it
memory_entry = MemoryEntry(
    id="custom_1",
    type=MemoryType.CUSTOM,
    content={"custom": "data"},
    timestamp=datetime.now(),
    importance=0.8
)
```

---

## Best Practices

### 1. Code Style

```python
# ✅ GOOD: Clear, documented, typed
def extract_keywords(self, text: str, top_n: int = 5) -> List[Tuple[str, float]]:
    """
    Extract keywords using KeyBERT.
    
    Args:
        text: Input text to analyze
        top_n: Number of keywords to extract
        
    Returns:
        List of (keyword, score) tuples
    """
    keywords = self.kw_model.extract_keywords(text, top_n=top_n)
    return keywords

# ❌ BAD: Unclear, no docs, no types
def extract(t, n=5):
    k = self.kw.extract(t, n)
    return k
```

### 2. Error Handling

```python
# ✅ GOOD: Specific exceptions, logging, graceful degradation
def fetch_article(self, url: str) -> Optional[str]:
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        return response.text
    except requests.exceptions.Timeout:
        logger.warning(f"Timeout fetching {url}")
        return None
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error {e.response.status_code}: {url}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return None

# ❌ BAD: Bare except, no logging
def fetch_article(url):
    try:
        return requests.get(url).text
    except:
        return None
```

### 3. Testing

```python
# ✅ GOOD: Clear test name, single responsibility, assertions
def test_duplicate_detection_with_similar_titles(memory_store):
    """Test that similar titles are detected as duplicates"""
    agent = WriterAgent(memory_store)
    
    # Setup
    title1 = "AI Breakthrough in Medicine"
    title2 = "Medicine AI Breakthrough"
    
    # Execute
    is_similar = agent._titles_similar(title1, title2)
    
    # Assert
    assert is_similar is True

# ❌ BAD: Unclear name, multiple tests in one, no assertions
def test_stuff(memory_store):
    agent = WriterAgent(memory_store)
    agent._titles_similar("a", "b")
    agent._check_if_already_generated("c", "d", [])
```

### 4. Memory Management

```python
# ✅ GOOD: Set appropriate importance, cleanup old entries
memory_entry = MemoryEntry(
    id=f"generation_{hash(title)}",
    type=MemoryType.SEMANTIC,
    content={"title": title, "url": url},
    timestamp=datetime.now(),
    importance=0.8  # High importance for duplicate detection
)
memory_store.store(memory_entry)

# Periodic cleanup
memory_store.cleanup(days=30)  # Remove entries older than 30 days

# ❌ BAD: All memories have same importance, no cleanup
memory_entry = MemoryEntry(..., importance=0.5)  # Everything is medium importance
# Never cleanup → database grows forever
```

---

## Quick Reference

### Running the System
```bash
python run.py
```

### Running Tests
```bash
pytest                    # All tests
pytest tests/test_agents.py  # Specific file
pytest -v                 # Verbose
pytest --cov=src          # With coverage
```

### Checking Code Quality
```bash
black src/ tests/         # Format code
flake8 src/ tests/        # Lint code
mypy src/                 # Type checking
```

### Debugging
```bash
LOG_LEVEL=DEBUG python run.py  # Debug logging
python -m pdb run.py           # Interactive debugger
```

### Common Commands
```bash
# View agent status
python -c "from src.orchestrator import Orchestrator; o = Orchestrator(); print(o.get_system_report())"

# Clear memory
rm -rf memory_store/

# Clear generated articles
rm -rf generated_articles/
```

---

## Next Steps

1. **Read the code**: Start with `src/agents/base.py`
2. **Run the system**: `python run.py`
3. **Make a small change**: Add a print statement
4. **Write a test**: Test your change
5. **Ask questions**: Team is here to help!

**Welcome aboard! Let's build amazing things together!** 🚀

