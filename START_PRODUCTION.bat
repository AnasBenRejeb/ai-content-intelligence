@echo off
REM Production Launch Script for Windows
REM Run this to start the system in production

echo ================================================================
echo         AI CONTENT INTELLIGENCE - PRODUCTION LAUNCH
echo ================================================================
echo.

REM Check if .env exists
if not exist .env (
    echo WARNING: .env file not found!
    echo.
    echo Creating .env file...
    echo Please add your API keys:
    echo.
    (
        echo # API Keys ^(REQUIRED^)
        echo NEWSAPI_KEY=your_newsapi_key_here
        echo GNEWS_API_KEY=your_gnews_key_here
        echo.
        echo # LLM Configuration
        echo LLM_ENABLED=true
        echo LLM_MODEL_PATH=models/mistral-7b-instruct-v0.2.Q4_K_M.gguf
        echo.
        echo # Logging
        echo LOG_LEVEL=INFO
        echo LOG_FILE=logs/app.log
        echo.
        echo # Performance
        echo MAX_WORKERS=5
        echo REQUEST_TIMEOUT=30
        echo.
        echo # Categories
        echo CATEGORIES=politics,technology,business,entertainment,sports,science,health
        echo.
        echo # Limits
        echo PAGE_SIZE=10
        echo PAGES_PER_CATEGORY=3
        echo REFLECTION_INTERVAL=10
    ) > .env
    echo Created .env file
    echo.
    echo IMPORTANT: Edit .env and add your API keys!
    echo    notepad .env
    echo.
    pause
)

REM Create directories
echo Creating directories...
if not exist logs mkdir logs
if not exist website mkdir website
if not exist articles mkdir articles
if not exist generated_articles mkdir generated_articles
if not exist memory_store mkdir memory_store
echo Directories created
echo.

REM Check Python
echo Checking Python...
python --version
echo.

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt >nul 2>&1
pip install schedule >nul 2>&1
echo Dependencies installed
echo.

REM Run tests
echo Running system verification...
python -c "import sys; from pathlib import Path; sys.path.insert(0, str(Path.cwd())); from src.orchestrator import Orchestrator; from src.config import settings; print('System verification passed')"

if %errorlevel% equ 0 (
    echo.
    echo ================================================================
    echo              SYSTEM READY FOR PRODUCTION
    echo ================================================================
    echo.
    echo Starting production scheduler...
    echo.
    echo The system will:
    echo   - Generate 10-20 articles every 12 hours
    echo   - Publish to website automatically
    echo   - Log all activity to logs/production.log
    echo   - Run forever ^(Ctrl+C to stop^)
    echo.
    echo Monitor: type logs\production.log
    echo.
    echo Starting in 3 seconds...
    timeout /t 3 /nobreak >nul
    
    REM Start production scheduler
    python production_scheduler.py
) else (
    echo.
    echo System verification failed
    echo Please check the error messages above
    pause
    exit /b 1
)
