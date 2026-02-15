# 🚀 Quick Start Guide

## Installation

### 1. Install Dependencies

```bash
pip install requests rapidfuzz keybert langdetect sentence-transformers pydantic pydantic-settings aiohttp tenacity rich
```

### 2. Set Up Environment

Create `.env` file:
```bash
NEWSAPI_KEY=b86bc01720554a51a966fc3c72af5dda
GNEWS_API_KEY=d41d8a047305a163373d164e3bb43cbe
```

## Running the System

### Basic Run

```bash
python -m src.main
```

### Run Demo

```bash
python demo.py
```

## Expected Output

```
🚀 Starting multi-agent news intelligence pipeline
📰 Phase 1: Collecting news titles
  CollectorAgent: Collected 145 unique titles
🔍 Phase 2: Analyzing titles and extracting keywords
  AnalyzerAgent: Analyzed 50 titles
📥 Phase 3: Retrieving full articles
  RetrieverAgent: Retrieved 20 articles
🧠 Performing metacognitive reflection
✨ Pipeline completed in 45.23s

✅ Pipeline completed successfully!
📊 Collected: 145 titles
🔍 Analyzed: 50 titles
📥 Retrieved: 20 articles
⏱️  Time: 45.23s
```

## What Happens

1. **CollectorAgent** fetches news titles from 4 categories
2. **AnalyzerAgent** extracts keywords from each title
3. **RetrieverAgent** searches and downloads full articles
4. All agents **reflect** on their performance
5. System generates a **comprehensive report**

## Output Files

- `articles/` - Retrieved article content
- `memory_store/` - Agent memories and learning

## Customization

Edit `src/config.py`:

```python
categories = ["politics", "technology"]  # Change categories
page_size = 100  # More articles per page
reflection_interval = 5  # Reflect more often
```

## Troubleshooting

**No articles retrieved?**
- Check API keys in `.env`
- Verify internet connection
- Check API rate limits

**Import errors?**
- Run: `pip install -r requirements.txt`

**Memory errors?**
- Clear: `rm -rf memory_store/`

## Next Steps

- Read [ARCHITECTURE.md](ARCHITECTURE.md) for system design
- Check [README.md](README.md) for full documentation
- Run tests: `pytest tests/`
- Explore agent code in `src/agents/`

Enjoy your intelligent news system! 🎉
