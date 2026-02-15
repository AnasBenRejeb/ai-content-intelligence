# 🚀 Deployment Guide

## Package Structure

The system is now fully packaged and ready for deployment:

```
news-intelligence-agents/
├── src/                    # Source code
│   ├── agents/            # Agent implementations
│   ├── memory/            # Memory system
│   ├── config.py          # Configuration
│   ├── orchestrator.py    # Orchestrator
│   └── main.py            # Entry point
├── tests/                 # Test suite
├── requirements.txt       # Dependencies
├── setup.py              # Package setup
├── README.md             # Documentation
├── ARCHITECTURE.md       # Architecture docs
├── QUICKSTART.md         # Quick start guide
└── .env.example          # Environment template
```

## Installation Methods

### Method 1: Direct Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Run directly
python -m src.main
```

### Method 2: Package Installation

```bash
# Install as package
pip install -e .

# Run using command
news-agents
```

### Method 3: Docker (Recommended for Production)

Create `Dockerfile`:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY .env .env

CMD ["python", "-m", "src.main"]
```

Build and run:

```bash
docker build -t news-agents .
docker run -v $(pwd)/articles:/app/articles news-agents
```

## Configuration

### Environment Variables

Create `.env` file:

```bash
NEWSAPI_KEY=your_key_here
GNEWS_API_KEY=your_key_here
LOG_LEVEL=INFO
MAX_WORKERS=5
```

### Custom Configuration

Edit `src/config.py` for advanced settings:

```python
class Settings(BaseSettings):
    categories: List[str] = ["politics", "technology"]
    reflection_interval: int = 10
    confidence_threshold: float = 0.7
```

## Production Deployment

### 1. Systemd Service (Linux)

Create `/etc/systemd/system/news-agents.service`:

```ini
[Unit]
Description=Multi-Agent News Intelligence System
After=network.target

[Service]
Type=simple
User=newsagent
WorkingDirectory=/opt/news-agents
ExecStart=/usr/bin/python3 -m src.main
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable news-agents
sudo systemctl start news-agents
```

### 2. Cron Job

Add to crontab:

```bash
# Run every hour
0 * * * * cd /path/to/news-agents && python -m src.main >> /var/log/news-agents.log 2>&1
```

### 3. Kubernetes

Create `deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: news-agents
spec:
  replicas: 1
  selector:
    matchLabels:
      app: news-agents
  template:
    metadata:
      labels:
        app: news-agents
    spec:
      containers:
      - name: news-agents
        image: news-agents:latest
        env:
        - name: NEWSAPI_KEY
          valueFrom:
            secretKeyRef:
              name: api-keys
              key: newsapi
        volumeMounts:
        - name: articles
          mountPath: /app/articles
      volumes:
      - name: articles
        persistentVolumeClaim:
          claimName: articles-pvc
```

## Monitoring

### Logging

Configure logging in production:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/news-agents.log'),
        logging.StreamHandler()
    ]
)
```

### Metrics

The system tracks:
- Total runs
- Success rate
- Articles collected/retrieved
- Agent performance
- Execution time

Access via:

```python
orchestrator = Orchestrator()
metrics = orchestrator.performance_metrics
```

## Scaling

### Horizontal Scaling

Run multiple instances with shared storage:

```bash
# Instance 1
python -m src.main --categories politics,technology

# Instance 2
python -m src.main --categories entertainment,sports
```

### Vertical Scaling

Increase workers:

```python
# In config.py
max_workers: int = 10  # More parallel processing
```

## Backup & Recovery

### Memory Backup

```bash
# Backup memory database
cp memory_store/shared_memory.db memory_store/backup_$(date +%Y%m%d).db

# Restore
cp memory_store/backup_20250101.db memory_store/shared_memory.db
```

### Article Backup

```bash
# Backup articles
tar -czf articles_backup_$(date +%Y%m%d).tar.gz articles/

# Restore
tar -xzf articles_backup_20250101.tar.gz
```

## Security

### API Key Management

Use environment variables or secrets management:

```bash
# AWS Secrets Manager
aws secretsmanager get-secret-value --secret-id newsapi-key

# HashiCorp Vault
vault kv get secret/newsapi
```

### File Permissions

```bash
chmod 600 .env
chmod 700 memory_store/
chmod 755 articles/
```

## Performance Tuning

### Database Optimization

```python
# In memory/base.py
cursor.execute("PRAGMA journal_mode=WAL")
cursor.execute("PRAGMA synchronous=NORMAL")
cursor.execute("PRAGMA cache_size=10000")
```

### Caching

Articles are automatically cached. Configure cache size:

```python
# In config.py
max_cache_size: int = 1000  # Max cached articles
cache_ttl: int = 86400  # 24 hours
```

## Troubleshooting

### Common Issues

**High memory usage:**
```bash
# Clear old memories
python -c "from src.memory.base import MemoryStore; m = MemoryStore('memory_store/shared_memory.db'); m.cleanup(days=30)"
```

**API rate limits:**
```python
# In config.py
request_delay: float = 1.0  # Delay between requests
```

**Disk space:**
```bash
# Clean old articles
find articles/ -mtime +30 -delete
```

## Health Checks

Create `healthcheck.py`:

```python
from src.orchestrator import Orchestrator

def health_check():
    try:
        orch = Orchestrator()
        statuses = orch.get_agent_statuses()
        return all(s['state'] != 'error' for s in statuses.values())
    except:
        return False

if __name__ == "__main__":
    exit(0 if health_check() else 1)
```

## Updates

### Rolling Updates

```bash
# Pull latest code
git pull origin main

# Install dependencies
pip install -r requirements.txt

# Restart service
sudo systemctl restart news-agents
```

### Zero-Downtime Updates

Use blue-green deployment with load balancer.

## Support

For issues:
1. Check logs: `/var/log/news-agents.log`
2. Review agent statuses: `orchestrator.get_system_report()`
3. Verify API keys and connectivity
4. Check disk space and memory

---

Your multi-agent system is now production-ready! 🎉
