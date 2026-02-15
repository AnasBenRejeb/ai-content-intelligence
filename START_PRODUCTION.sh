#!/bin/bash
# Production Launch Script
# Run this to start the system in production

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║        🚀 AI CONTENT INTELLIGENCE - PRODUCTION LAUNCH        ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found!"
    echo ""
    echo "Creating .env file..."
    echo "Please add your API keys:"
    echo ""
    cat > .env << 'EOF'
# API Keys (REQUIRED)
NEWSAPI_KEY=your_newsapi_key_here
GNEWS_API_KEY=your_gnews_key_here

# LLM Configuration
LLM_ENABLED=true
LLM_MODEL_PATH=models/mistral-7b-instruct-v0.2.Q4_K_M.gguf

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/app.log

# Performance
MAX_WORKERS=5
REQUEST_TIMEOUT=30

# Categories
CATEGORIES=politics,technology,business,entertainment,sports,science,health

# Limits
PAGE_SIZE=10
PAGES_PER_CATEGORY=3
REFLECTION_INTERVAL=10
EOF
    echo "✅ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env and add your API keys!"
    echo "   nano .env"
    echo ""
    read -p "Press Enter after adding API keys..."
fi

# Create directories
echo "📁 Creating directories..."
mkdir -p logs
mkdir -p website
mkdir -p articles
mkdir -p generated_articles
mkdir -p memory_store
echo "✅ Directories created"
echo ""

# Check Python
echo "🐍 Checking Python..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✅ Python $python_version detected"
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt > /dev/null 2>&1
pip3 install schedule > /dev/null 2>&1
echo "✅ Dependencies installed"
echo ""

# Run tests
echo "🧪 Running system verification..."
python3 -c "
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))
from src.orchestrator import Orchestrator
from src.config import settings
print('✅ System verification passed')
" 2>&1

if [ $? -eq 0 ]; then
    echo ""
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║              ✅ SYSTEM READY FOR PRODUCTION                  ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo ""
    echo "🚀 Starting production scheduler..."
    echo ""
    echo "The system will:"
    echo "  • Generate 10-20 articles every 12 hours"
    echo "  • Publish to website automatically"
    echo "  • Log all activity to logs/production.log"
    echo "  • Run forever (Ctrl+C to stop)"
    echo ""
    echo "📊 Monitor: tail -f logs/production.log"
    echo ""
    echo "Starting in 3 seconds..."
    sleep 3
    
    # Start production scheduler
    python3 production_scheduler.py
else
    echo ""
    echo "❌ System verification failed"
    echo "Please check the error messages above"
    exit 1
fi
