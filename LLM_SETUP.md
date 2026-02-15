# 🤖 LLM Setup Guide

## Overview

The WriterAgent uses a local LLM (Mistral-7B) to generate articles based on retrieved content. This is optional but adds powerful content generation capabilities.

## Quick Setup

### Option 1: Automatic Setup (Recommended)

```bash
python setup_llm.py
```

This will:
1. Install llama-cpp-python
2. Download the Mistral-7B model (~4GB)
3. Configure the system

### Option 2: Manual Setup

1. **Install llama-cpp-python**
```bash
pip install llama-cpp-python
```

2. **Download Model**

Download a GGUF model (recommended: Mistral-7B Q4_K_M):
- From HuggingFace: https://huggingface.co/TheBloke/Mistral-7B-v0.3-GGUF
- Or use your existing model

3. **Place Model**
```
models/
└── mistral-7b-v0.3-sarcasm-scrolls-4k-q4_k_m.gguf
```

4. **Configure**

Edit `.env`:
```bash
LLM_MODEL_PATH=models/your-model.gguf
LLM_ENABLED=true
```

## Using Your Existing Model

If you already have the Mistral model from your notebooks:

```bash
# Copy your existing model
mkdir -p models
cp "C:/path/to/your/mistral-7b-v0.3-sarcasm-scrolls-4k-q4_k_m.gguf" models/
```

Update `src/config.py`:
```python
llm_model_path: str = "models/mistral-7b-v0.3-sarcasm-scrolls-4k-q4_k_m.gguf"
```

## Running Without LLM

The system works perfectly without LLM - it just won't generate new articles.

To disable:
```bash
# In .env
LLM_ENABLED=false
```

Or in `src/config.py`:
```python
llm_enabled: bool = False
```

## How It Works

### With LLM Enabled

```
Retrieved Article → WriterAgent → LLM Generation → New Article
```

The WriterAgent:
1. Takes retrieved article content
2. Creates a prompt for the LLM
3. Generates a new article (300-500 words)
4. Saves to `generated_articles/`

### Without LLM

```
Retrieved Article → WriterAgent → Template Generation → Basic Article
```

Falls back to template-based generation.

## Configuration

### Model Settings

In `src/config.py`:
```python
# LLM configuration
llm_model_path: str = "models/mistral-7b-v0.3.gguf"
llm_enabled: bool = True
```

### Generation Parameters

In `src/agents/writer.py`:
```python
response = self.llm(
    prompt,
    max_tokens=1000,      # Article length
    temperature=0.7,      # Creativity (0.0-1.0)
    top_p=0.9,           # Diversity
    stop=["</article>"]  # Stop sequences
)
```

## GPU Acceleration (Optional)

For faster generation with GPU:

```bash
# Install with CUDA support
CMAKE_ARGS="-DLLAMA_CUBLAS=on" pip install llama-cpp-python
```

Then in `src/agents/writer.py`:
```python
self.llm = Llama(
    model_path=str(self.model_path),
    n_ctx=4096,
    n_threads=4,
    n_gpu_layers=35  # Use GPU for 35 layers
)
```

## Troubleshooting

### Model Not Found
```
WARNING: LLM model not found at models/...
WriterAgent will operate in mock mode
```

**Solution**: Download model or disable LLM

### Out of Memory
```
Error: Failed to allocate memory
```

**Solution**: Use smaller model (Q4_K_S instead of Q4_K_M)

### Slow Generation
```
Generation taking >30 seconds per article
```

**Solutions**:
- Use GPU acceleration
- Reduce max_tokens
- Use smaller model

## Model Recommendations

### For CPU (4-8GB RAM)
- Mistral-7B Q4_K_S (~3.5GB)
- Llama-2-7B Q4_0 (~3.5GB)

### For CPU (16GB+ RAM)
- Mistral-7B Q4_K_M (~4.1GB)
- Llama-2-13B Q4_0 (~7GB)

### For GPU (8GB+ VRAM)
- Mistral-7B Q5_K_M (~4.8GB)
- Llama-2-13B Q4_K_M (~7.4GB)

## Example Output

### With LLM
```
✍️  Phase 4: Generating new articles with LLM
  → WriterAgent: Using local LLM for generation
  → Generated article: "AI Breakthrough in Medical Diagnosis"
  → Word count: 487
  → Saved to: generated_articles/AI_Breakthrough_in_Medical_Diagnosis.md
✅ Generated 10 articles
```

### Without LLM
```
⏭️  Phase 4: Skipped (LLM disabled in config)
```

## Performance

### Generation Speed
- CPU (4 cores): ~20-30 seconds per article
- CPU (8 cores): ~10-15 seconds per article
- GPU (RTX 3060): ~2-5 seconds per article

### Quality
- LLM-generated: High quality, contextual
- Template-based: Basic structure, generic content

## Advanced: Custom Prompts

Edit `src/agents/writer.py` to customize prompts:

```python
def _create_prompt(self, title: str, source_content: str = "") -> str:
    prompt = f"""<s>[INST] You are a professional journalist...

Title: {title}

Write in the style of: [YOUR STYLE]
Focus on: [YOUR FOCUS]
Tone: [YOUR TONE]

Article: [/INST]
"""
    return prompt
```

## Integration with Pipeline

The WriterAgent is automatically integrated:

```python
orchestrator = Orchestrator()
result = orchestrator.run_pipeline()

# Check generated articles
print(f"Generated: {result['generated_count']} articles")
```

## Next Steps

1. Run `python setup_llm.py`
2. Execute `python run.py`
3. Check `generated_articles/` for output
4. Customize prompts as needed

---

**Note**: LLM generation is optional. The system works great without it for collection, analysis, and retrieval!
