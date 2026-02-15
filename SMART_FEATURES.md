# 🧠 Smart Duplicate Detection & Memory Features

## Overview

The system now has **intelligent duplicate detection** that prevents generating the same article twice, even across multiple runs!

## How It Works

### 1. Multi-Level Duplicate Detection

The WriterAgent checks for duplicates using **three methods**:

#### Method 1: Title Similarity (85% threshold)
```python
# Uses fuzzy matching to detect similar titles
"AI Breakthrough in Medicine" ≈ "AI Breakthrough in Medical Field"
→ Detected as duplicate, skipped
```

#### Method 2: Source URL Matching
```python
# Tracks source URLs in memory
Source: "https://example.com/article-123"
→ Already generated from this URL
→ Skipped
```

#### Method 3: File Existence Check
```python
# Checks if file already exists
generated_articles/AI_Breakthrough_in_Medicine.md exists
→ Skipped
```

### 2. Persistent Memory

Every generated article is stored in memory with:
- **Title**: For similarity matching
- **Source URL**: For exact source tracking
- **Content Hash**: MD5 hash of generated content
- **Timestamp**: When it was generated
- **Metadata**: Word count, method, model used

### 3. Metadata Files

Each generated article gets a metadata file:

```json
{
  "title": "AI Breakthrough in Medical Diagnosis",
  "source_url": "https://example.com/article",
  "generated_at": "2025-02-15T10:30:00",
  "word_count": 487,
  "content_hash": "a1b2c3d4e5f6...",
  "agent": "WriterAgent",
  "model": "mistral-7b"
}
```

## Example Flow

### First Run
```
📥 Retrieved: "AI Breakthrough in Medicine"
✍️  Thinking: Should I generate?
  → Checking memory... No previous generation found
  → Checking file system... File doesn't exist
  → Decision: Generate new article
✅ Generated: AI_Breakthrough_in_Medicine.md
💾 Stored in memory with metadata
```

### Second Run (Same Article)
```
📥 Retrieved: "AI Breakthrough in Medicine"
✍️  Thinking: Should I generate?
  → Checking memory... Found previous generation!
  → Title: "AI Breakthrough in Medicine"
  → Generated: 2025-02-15T10:30:00
  → Decision: Skip duplicate
⏭️  Skipped: Already generated from this source
```

### Second Run (Similar Title)
```
📥 Retrieved: "AI Breakthrough in Medical Field"
✍️  Thinking: Should I generate?
  → Checking memory... Checking similarity...
  → 92% similar to "AI Breakthrough in Medicine"
  → Decision: Skip duplicate
⏭️  Skipped: Too similar to existing article
```

## Smart Features

### 1. Cross-Run Memory
```python
# Memory persists across runs
Run 1: Generate 10 articles → Stored in memory
Run 2: System remembers all 10 → Won't regenerate
Run 3: Still remembers → Continues to skip
```

### 2. Intelligent Reasoning
```python
# Agent explains its decisions
Thought: "Generate article: AI Breakthrough..."
Reasoning:
  1. "Generating article for: AI Breakthrough in Medicine"
  2. "Source content length: 2500 chars"
  3. "⚠️  Already generated article from this source!"
  4. "Will skip to avoid duplication"
Confidence: 0.95
Decision: Skip
```

### 3. Learning from Patterns
```python
# Agent learns what makes duplicates
Pattern 1: "Articles with 85%+ title similarity are duplicates"
Pattern 2: "Same source URL = same article"
Pattern 3: "Content hash collision = exact duplicate"
→ Stored in self-model for future use
```

### 4. Batch Processing with Stats
```
Processing 20 articles:
✅ Generated: "AI in Healthcare" (1/20)
✅ Generated: "Climate Change Impact" (2/20)
⏭️  Skipped duplicate (1 total)
✅ Generated: "Tech Innovation" (3/20)
⏭️  Skipped duplicate (2 total)
...
📊 Final: 15 articles generated, 5 duplicates skipped
```

## Configuration

### Similarity Threshold

In `src/agents/writer.py`:
```python
def _titles_similar(self, title1: str, title2: str, threshold: int = 85):
    """Adjust threshold for stricter/looser matching"""
    # 85 = default (recommended)
    # 90 = stricter (fewer false positives)
    # 80 = looser (more aggressive deduplication)
```

### Memory Importance

```python
memory_entry = MemoryEntry(
    importance=0.8  # High importance = never forgotten
)
```

## Output Examples

### Terminal Output
```
✍️  Phase 4: Generating new articles with LLM
  → WriterAgent: Using local LLM for generation
  
  Processing article 1/20...
  ✅ Generated: "AI Breakthrough in Medicine" (487 words)
  
  Processing article 2/20...
  ⏭️  Skipped: Already generated from this source
  
  Processing article 3/20...
  ✅ Generated: "Climate Change Solutions" (512 words)
  
  ...
  
📊 Final: 15 articles generated, 5 duplicates skipped
```

### Metadata File
```
generated_articles/
├── AI_Breakthrough_in_Medicine.md
├── AI_Breakthrough_in_Medicine_metadata.json
├── Climate_Change_Solutions.md
└── Climate_Change_Solutions_metadata.json
```

### Memory Database
```sql
SELECT * FROM memories WHERE type='semantic' 
  AND content LIKE '%generate_article%';

Results:
- Title: "AI Breakthrough in Medicine"
  Source: "https://example.com/ai-article"
  Hash: "a1b2c3d4..."
  Timestamp: 2025-02-15 10:30:00
  
- Title: "Climate Change Solutions"
  Source: "https://example.com/climate"
  Hash: "e5f6g7h8..."
  Timestamp: 2025-02-15 10:31:15
```

## Benefits

### 1. No Duplicate Content
- Never generates the same article twice
- Saves processing time and resources
- Maintains content uniqueness

### 2. Efficient Processing
- Skips duplicates instantly
- No wasted LLM inference
- Faster batch processing

### 3. Smart Learning
- Learns from past generations
- Improves duplicate detection over time
- Adapts to patterns

### 4. Transparent Operation
- Clear reasoning for each decision
- Detailed logging
- Metadata for auditing

## Advanced Features

### Content Hash Comparison
```python
# Even if titles differ, identical content is detected
Article 1: "AI in Healthcare" → Hash: abc123
Article 2: "Healthcare AI" → Hash: abc123
→ Detected as duplicate by content hash
```

### URL Tracking
```python
# Tracks source URLs across runs
Memory: {
  "https://example.com/article-1": "Generated 2025-02-15",
  "https://example.com/article-2": "Generated 2025-02-15",
  "https://example.com/article-3": "Generated 2025-02-15"
}
→ Won't fetch from these URLs again
```

### Fuzzy Title Matching
```python
# Handles variations
"AI Breakthrough" vs "AI breakthrough" → Match
"AI Breakthrough" vs "A.I. Breakthrough" → Match
"AI Breakthrough" vs "Artificial Intelligence Breakthrough" → Match (if >85%)
```

## Troubleshooting

### Too Many Skips?
```python
# Lower similarity threshold
threshold: int = 80  # More lenient
```

### Not Enough Skips?
```python
# Raise similarity threshold
threshold: int = 90  # Stricter matching
```

### Clear Memory
```python
# To start fresh
rm -rf memory_store/
python run.py  # Rebuilds memory
```

## Statistics

The system tracks:
- Total articles processed
- Articles generated
- Duplicates skipped
- Skip reasons (title/URL/file)
- Processing time saved

## Example Session

```
Run 1 (Fresh start):
- Processed: 20 articles
- Generated: 20 articles
- Skipped: 0 duplicates
- Time: 180 seconds

Run 2 (Same sources):
- Processed: 20 articles
- Generated: 0 articles
- Skipped: 20 duplicates (all from memory)
- Time: 5 seconds (36x faster!)

Run 3 (Mixed sources):
- Processed: 20 articles
- Generated: 12 articles (new)
- Skipped: 8 duplicates (from memory)
- Time: 110 seconds
```

## Integration with Other Agents

### CollectorAgent
- Deduplicates titles before passing to analyzer
- Prevents duplicate collection

### AnalyzerAgent
- Stores keyword analyses in memory
- Reuses analyses for similar titles

### RetrieverAgent
- Caches retrieved articles
- Checks cache before fetching

### WriterAgent
- Checks all previous generations
- Skips duplicates intelligently
- Stores metadata for future runs

## Summary

Your system now has **enterprise-grade duplicate detection**:

✅ **Multi-level checking** (title, URL, file, content)
✅ **Persistent memory** (survives restarts)
✅ **Fuzzy matching** (handles variations)
✅ **Metadata tracking** (full audit trail)
✅ **Smart reasoning** (explains decisions)
✅ **Learning capability** (improves over time)
✅ **Efficient processing** (skips instantly)
✅ **Transparent operation** (detailed logging)

**Result**: Never generates duplicate articles, even across multiple runs! 🎉
