@echo off
echo.
echo ========================================
echo   OPENING DEPLOYMENT SITES
echo ========================================
echo.
echo Opening GitHub (create repository)...
start https://github.com/new
timeout /t 2 /nobreak >nul

echo Opening Render (deploy platform)...
start https://render.com/register
timeout /t 2 /nobreak >nul

echo.
echo ========================================
echo   SITES OPENED!
echo ========================================
echo.
echo NEXT STEPS:
echo 1. Create GitHub repository: ai-content-intelligence
echo 2. Sign up for Render with GitHub
echo 3. Follow FINAL_DEPLOYMENT_STEPS.md
echo.
echo Your git is ready! Just push to GitHub.
echo.
pause
