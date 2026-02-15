# 🚀 Complete Execution Guide

## For Operations Teams & System Administrators

This guide provides **everything you need** to execute the Multi-Agent News Intelligence System smoothly in any environment.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Execution Methods](#execution-methods)
5. [Monitoring & Logs](#monitoring--logs)
6. [Troubleshooting](#troubleshooting)
7. [Maintenance](#maintenance)
8. [Performance Tuning](#performance-tuning)
9. [Backup & Recovery](#backup--recovery)
10. [Security](#security)

---

## Prerequisites

### System Requirements

**Minimum:**
- OS: Linux (Ubuntu 20.04+), macOS (10.15+), Windows 10+
- CPU: 2 cores
- RAM: 4 GB
- Disk: 10 GB free space
- Python: 3.8 or higher

**Recommended:**
- OS: Linux (Ubuntu 22.04)
- CPU: 4+ cores
- RAM: 8+ GB
- Disk: 50+ GB SSD
- Python: 3.10 or higher

**For LLM Generation:**
- CPU: 8+ cores OR GPU (NVIDIA with CUDA)
- RAM: 16+ GB
- Disk: 20+ GB for model storage

### Required API Keys

1. **NewsAPI** (Free tier available)
   - Sign up: https://newsapi.org/register
   - Free: 100 requests/day
   - Paid: Unlimited requests

2. **GNews API** (Free tier available)
   - Sign up: https://gnews.io/register
   - Free: 100 requests/day
   - Paid: Up to 100,000 requests/day

### Software Dependencies

```bash
# Check Python version
python --version  # Should be 3.8+

# Check pip
pip --version

# Optional: Check Docker
docker --version
```

---

## Installation

### Method 1: Quick Install (Recommended)

**Linux/macOS:**
```bash
# Clone repository
git clone <repository-url>
cd news-intelligence-agents

# Make installer executable
chmod +x install.sh

# Run installer
./install.sh

# Verify installation
python -c "import src; print('✅ Installation successful!')"
```

**Windows:**
```cmd
REM Clone repository
git clone <repository-url>
cd news-intelligence-agents

REM Run installer
install.bat

REM Verify installation
python -c "import src; print('✅ Installation successful!')"
```

### Method 2: Manual Installation

```bash
# 1. Clone repository
git clone <repository-url>
cd news-intelligence-agents

# 2. Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# Linux/macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Install package in development mode
pip install -e .

# 5. Verify installation
python -c "from src.orchestrator import Orchestrator; print('✅ Success!')"
```

### Method 3: Docker Installation

```bash
# 1. Clone repository
git clone <repository-url>
cd news-intelligence-agents

# 2. Build Docker image
docker build -t news-agents:latest .

# 3. Verify image
docker images | grep news-agents
```

### Method 4: Production Installation

```bash
# For production servers
sudo pip install news-intelligence-agents

# Or from wheel
pip install dist/news_intelligence_agents-1.2.0-py3-none-any.whl
```

---

## Configuration

### Step 1: Environment Variables

```bash
# Copy example environment file
cp .env.example .env

# Edit configuration
nano .env  # or vim .env or notepad .env
```

**Required Configuration:**

```bash
# API Keys (REQUIRED)
NEWSAPI_KEY=your_newsapi_key_here
GNEWS_API_KEY=your_gnews_key_here

# LLM Configuration (OPTIONAL)
LLM_ENABLED=true
LLM_MODEL_PATH=models/mistral-7b-instruct-v0.2.Q4_K_M.gguf

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/app.log

# Performance
MAX_WORKERS=5
REQUEST_TIMEOUT=30

# Categories to collect
CATEGORIES=politics,technology,business,entertainment,sports,science,health

# Limits
PAGE_SIZE=10
PAGES_PER_CATEGORY=3
REFLECTION_INTERVAL=10
```

### Step 2: LLM Setup (Optional but Recommended)

**If you want AI article generation:**

```bash
# Run LLM setup script
python setup_llm.py

# This will:
# 1. Create models/ directory
# 2. Download Mistral-7B model (~4GB)
# 3. Verify installation
# 4. Test generation

# Manual download (if script fails):
mkdir -p models
cd models
wget https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q4_K_M.gguf
cd ..
```

**If you DON'T want LLM generation:**

```bash
# In .env file, set:
LLM_ENABLED=false

# System will use template-based generation instead
```

### Step 3: Directory Structure

```bash
# Create required directories
mkdir -p articles
mkdir -p generated_articles
mkdir -p memory_store
mkdir -p logs

# Set permissions (Linux/macOS)
chmod 755 articles generated_articles memory_store
chmod 644 .env
```

### Step 4: Verify Configuration

```bash
# Test configuration
python -c "
from src.config import settings
print(f'✅ NewsAPI Key: {settings.newsapi_key[:10]}...')
print(f'✅ GNews Key: {settings.gnews_api_key[:10]}...')
print(f'✅ LLM Enabled: {settings.llm_enabled}')
print(f'✅ Categories: {settings.categories}')
"
```

---

## Execution Methods

### Method 1: Direct Execution (Development)

```bash
# Simple run
python run.py

# With custom log level
LOG_LEVEL=DEBUG python run.py

# With specific categories
CATEGORIES=technology,science python run.py
```

### Method 2: Package Command (After pip install)

```bash
# Run using CLI command
news-agents

# With options
news-agents --log-level DEBUG
news-agents --categories technology,science
```

### Method 3: Module Execution

```bash
# Run as Python module
python -m src.main

# With arguments
python -m src.main --help
```

### Method 4: Docker Execution

```bash
# Run in Docker container
docker run -d \
  --name news-agents \
  -v $(pwd)/articles:/app/articles \
  -v $(pwd)/generated_articles:/app/generated_articles \
  -v $(pwd)/memory_store:/app/memory_store \
  -e NEWSAPI_KEY=your_key \
  -e GNEWS_API_KEY=your_key \
  news-agents:latest

# View logs
docker logs -f news-agents

# Stop container
docker stop news-agents

# Remove container
docker rm news-agents
```

### Method 5: Scheduled Execution (Production)

**Linux/macOS (Cron):**

```bash
# Edit crontab
crontab -e

# Add scheduled job (runs every hour)
0 * * * * cd /path/to/news-agents && /usr/bin/python run.py >> /var/log/news-agents.log 2>&1

# Run every 6 hours
0 */6 * * * cd /path/to/news-agents && /usr/bin/python run.py >> /var/log/news-agents.log 2>&1

# Run daily at 2 AM
0 2 * * * cd /path/to/news-agents && /usr/bin/python run.py >> /var/log/news-agents.log 2>&1
```

**Windows (Task Scheduler):**

```powershell
# Create scheduled task
$action = New-ScheduledTaskAction -Execute "python" -Argument "C:\path\to\news-agents\run.py"
$trigger = New-ScheduledTaskTrigger -Daily -At 2am
Register-ScheduledTask -Action $action -Trigger $trigger -TaskName "NewsAgents" -Description "Run news intelligence system"
```

**Systemd Service (Linux):**

```bash
# Create service file
sudo nano /etc/systemd/system/news-agents.service

# Add content:
[Unit]
Description=Multi-Agent News Intelligence System
After=network.target

[Service]
Type=simple
User=newsagent
WorkingDirectory=/opt/news-agents
Environment="PATH=/opt/news-agents/venv/bin"
ExecStart=/opt/news-agents/venv/bin/python run.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target

# Enable and start
sudo systemctl enable news-agents
sudo systemctl start news-agents
sudo systemctl status news-agents
```

### Method 6: Demo Execution

```bash
# Run interactive demo
python demo.py

# Shows:
# - Agent initialization
# - Pipeline execution
# - Memory system
# - Self-reference capabilities
# - Learning process
```

---

## Monitoring & Logs

### Log Locations

```bash
# Application logs
logs/app.log

# System logs (if using systemd)
sudo journalctl -u news-agents -f

# Docker logs
docker logs -f news-agents
```

### Log Levels

```bash
# DEBUG - Detailed information
LOG_LEVEL=DEBUG python run.py

# INFO - General information (default)
LOG_LEVEL=INFO python run.py

# WARNING - Warning messages only
LOG_LEVEL=WARNING python run.py

# ERROR - Error messages only
LOG_LEVEL=ERROR python run.py
```

### Real-time Monitoring

```bash
# Watch log file
tail -f logs/app.log

# Watch with grep filter
tail -f logs/app.log | grep "ERROR"

# Watch generated articles
watch -n 5 'ls -lh generated_articles/ | tail -10'

# Monitor memory usage
watch -n 2 'du -sh memory_store/'
```

### System Status

```bash
# Check system status
python -c "
from src.orchestrator import Orchestrator
orch = Orchestrator()
print(orch.get_system_report())
"

# Check agent statuses
python -c "
from src.orchestrator import Orchestrator
orch = Orchestrator()
statuses = orch.get_agent_statuses()
for name, status in statuses.items():
    print(f'{name}: {status[\"state\"]} - Success: {status[\"success_rate\"]:.1%}')
"
```

### Performance Metrics

```bash
# View performance metrics
python -c "
from src.orchestrator import Orchestrator
orch = Orchestrator()
metrics = orch.performance_metrics
for key, value in metrics.items():
    print(f'{key}: {value}')
"
```

---

## Troubleshooting

### Common Issues

#### Issue 1: API Key Errors

**Symptom:**
```
ERROR: Invalid API key
```

**Solution:**
```bash
# Verify API keys
echo $NEWSAPI_KEY
echo $GNEWS_API_KEY

# Re-check .env file
cat .env | grep API_KEY

# Test API keys
curl "https://newsapi.org/v2/top-headlines?country=us&apiKey=YOUR_KEY"
```

#### Issue 2: Import Errors

**Symptom:**
```
ModuleNotFoundError: No module named 'src'
```

**Solution:**
```bash
# Reinstall dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .

# Check Python path
python -c "import sys; print('\n'.join(sys.path))"
```

#### Issue 3: LLM Not Loading

**Symptom:**
```
WARNING: LLM model not found
```

**Solution:**
```bash
# Check model file exists
ls -lh models/mistral-7b-instruct-v0.2.Q4_K_M.gguf

# Re-download model
python setup_llm.py

# Or disable LLM
echo "LLM_ENABLED=false" >> .env
```

#### Issue 4: Memory/Disk Issues

**Symptom:**
```
ERROR: No space left on device
```

**Solution:**
```bash
# Check disk space
df -h

# Clean old articles
find articles/ -mtime +30 -delete
find generated_articles/ -mtime +30 -delete

# Clean memory database
python -c "
from src.memory.base import MemoryStore
m = MemoryStore('memory_store/shared_memory.db')
m.cleanup(days=30)
"
```

#### Issue 5: Rate Limiting

**Symptom:**
```
ERROR: 429 Too Many Requests
```

**Solution:**
```bash
# Reduce request frequency in .env
REQUEST_DELAY=2.0
PAGES_PER_CATEGORY=2

# Or upgrade API plan
```

#### Issue 6: Permission Errors

**Symptom:**
```
PermissionError: [Errno 13] Permission denied
```

**Solution:**
```bash
# Fix permissions (Linux/macOS)
chmod 755 articles generated_articles memory_store
chmod 644 .env

# Run as correct user
sudo chown -R $USER:$USER .
```

### Debug Mode

```bash
# Run in debug mode
LOG_LEVEL=DEBUG python run.py 2>&1 | tee debug.log

# Check all components
python -c "
import logging
logging.basicConfig(level=logging.DEBUG)

from src.orchestrator import Orchestrator
from src.config import settings

print('Config:', settings.dict())
orch = Orchestrator()
print('Agents:', [a.name for a in orch.agents])
"
```

### Health Check

```bash
# Create health check script
cat > healthcheck.sh << 'EOF'
#!/bin/bash
python -c "
from src.orchestrator import Orchestrator
try:
    orch = Orchestrator()
    statuses = orch.get_agent_statuses()
    if all(s['state'] != 'error' for s in statuses.values()):
        print('✅ System healthy')
        exit(0)
    else:
        print('❌ System unhealthy')
        exit(1)
except Exception as e:
    print(f'❌ Error: {e}')
    exit(1)
"
EOF

chmod +x healthcheck.sh
./healthcheck.sh
```

---

## Maintenance

### Daily Maintenance

```bash
# Check logs for errors
grep -i error logs/app.log | tail -20

# Check disk usage
du -sh articles/ generated_articles/ memory_store/

# Verify system health
./healthcheck.sh
```

### Weekly Maintenance

```bash
# Backup memory database
cp memory_store/shared_memory.db memory_store/backup_$(date +%Y%m%d).db

# Clean old backups (keep last 4 weeks)
find memory_store/ -name "backup_*.db" -mtime +28 -delete

# Update dependencies
pip list --outdated
```

### Monthly Maintenance

```bash
# Full backup
tar -czf backup_$(date +%Y%m%d).tar.gz \
  articles/ \
  generated_articles/ \
  memory_store/ \
  .env

# Clean old articles (keep last 60 days)
find articles/ -mtime +60 -delete
find generated_articles/ -mtime +60 -delete

# Optimize memory database
python -c "
from src.memory.base import MemoryStore
m = MemoryStore('memory_store/shared_memory.db')
m.cleanup(days=60)
"

# Update system
git pull origin main
pip install -r requirements.txt --upgrade
```

---

## Performance Tuning

### CPU Optimization

```bash
# Increase worker threads (in .env)
MAX_WORKERS=10  # For 8+ core systems

# Reduce for low-end systems
MAX_WORKERS=2
```

### Memory Optimization

```bash
# Limit batch sizes (in .env)
PAGE_SIZE=5
PAGES_PER_CATEGORY=2

# Clean memory more frequently
REFLECTION_INTERVAL=5
```

### Network Optimization

```bash
# Adjust timeouts (in .env)
REQUEST_TIMEOUT=15  # Faster timeout
REQUEST_DELAY=0.5   # Less delay between requests

# For slow networks
REQUEST_TIMEOUT=60
REQUEST_DELAY=2.0
```

### LLM Optimization

```bash
# Use GPU if available (in src/agents/writer.py)
n_gpu_layers=35  # Offload to GPU

# Reduce context for faster generation
n_ctx=2048  # Instead of 4096

# Use smaller model
# Download: mistral-7b-instruct-v0.2.Q3_K_M.gguf (smaller, faster)
```

---

## Backup & Recovery

### Backup Strategy

```bash
# Full backup script
cat > backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/backups/news-agents"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup data
tar -czf $BACKUP_DIR/data_$DATE.tar.gz \
  articles/ \
  generated_articles/ \
  memory_store/

# Backup config
cp .env $BACKUP_DIR/env_$DATE

# Keep last 7 days
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "✅ Backup completed: $BACKUP_DIR/data_$DATE.tar.gz"
EOF

chmod +x backup.sh
```

### Recovery Procedure

```bash
# Restore from backup
tar -xzf /backups/news-agents/data_20250215_120000.tar.gz

# Restore config
cp /backups/news-agents/env_20250215 .env

# Verify restoration
python -c "
from src.orchestrator import Orchestrator
orch = Orchestrator()
print('✅ System restored successfully')
"
```

---

## Security

### API Key Security

```bash
# Secure .env file
chmod 600 .env

# Never commit .env to git
echo ".env" >> .gitignore

# Use environment variables in production
export NEWSAPI_KEY="your_key"
export GNEWS_API_KEY="your_key"
```

### File Permissions

```bash
# Secure directories
chmod 700 memory_store/
chmod 755 articles/ generated_articles/

# Secure scripts
chmod 700 *.sh
```

### Network Security

```bash
# Use HTTPS only (already configured)
# Verify SSL certificates (already enabled)

# For production, use firewall
sudo ufw allow 22/tcp  # SSH only
sudo ufw enable
```

---

## Quick Reference

### Start System
```bash
python run.py
```

### Stop System
```bash
# If running in foreground: Ctrl+C
# If systemd: sudo systemctl stop news-agents
# If Docker: docker stop news-agents
```

### Check Status
```bash
./healthcheck.sh
```

### View Logs
```bash
tail -f logs/app.log
```

### Backup
```bash
./backup.sh
```

### Update
```bash
git pull && pip install -r requirements.txt
```

---

## Support Checklist

Before requesting support, verify:

- [ ] Python 3.8+ installed
- [ ] All dependencies installed (`pip list`)
- [ ] API keys configured in `.env`
- [ ] Directories created and writable
- [ ] No disk space issues (`df -h`)
- [ ] Logs checked for errors (`tail logs/app.log`)
- [ ] Health check passed (`./healthcheck.sh`)

---

**System is ready for smooth execution!** 🚀
