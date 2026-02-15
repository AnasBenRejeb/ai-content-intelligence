@echo off
REM Quick Launch Script for Windows
REM This will test and start the production system

echo ========================================
echo   AI CONTENT INTELLIGENCE PLATFORM
echo   Quick Launch Script
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Please install Python 3.8+ from python.org
    pause
    exit /b 1
)

echo [1/4] Testing system...
python test_system.py
if errorlevel 1 (
    echo.
    echo ERROR: System test failed!
    echo Please fix the issues above before launching.
    pause
    exit /b 1
)

echo.
echo [2/4] Creating required directories...
if not exist "logs" mkdir logs
if not exist "memory_store" mkdir memory_store
if not exist "articles" mkdir articles
if not exist "generated_articles" mkdir generated_articles
echo Done!

echo.
echo [3/4] Checking .env file...
if not exist ".env" (
    echo WARNING: .env file not found!
    echo Creating from .env.example...
    copy .env.example .env
    echo.
    echo IMPORTANT: Edit .env and add your API keys!
    echo Press any key to open .env in notepad...
    pause >nul
    notepad .env
    echo.
    echo After adding your API keys, press any key to continue...
    pause >nul
)

echo.
echo [4/4] Starting production scheduler...
echo.
echo ========================================
echo   SYSTEM STARTING
echo ========================================
echo.
echo The system will:
echo - Generate articles every 12 hours
echo - Auto-publish to website
echo - Log everything to logs/production.log
echo.
echo Press Ctrl+C to stop the system
echo.
echo ========================================
echo.

python production_scheduler.py

pause
