@echo off
title Paper Polish Tool
color 0A

echo ========================================
echo       Paper Polish Tool - Optimized
echo ========================================
echo.

echo [1/4] Checking Python...
python --version
if %errorlevel% neq 0 (
    echo [Error] Python not found!
    pause
    exit /b 1
)

echo [2/4] Checking Node.js...
node --version
if %errorlevel% neq 0 (
    echo [Error] Node.js not found!
    pause
    exit /b 1
)

echo [3/4] Installing backend dependencies...
cd /d "%~dp0backend"
pip install -r requirements.txt -q
echo Done.

echo [4/4] Installing frontend dependencies...
cd /d "%~dp0frontend"
call npm install --silent
echo Done.

echo.
echo ========================================
echo   Starting services with optimizations:
echo   - Text splitting & parallel processing
echo   - LRU cache for repeated requests
echo   - Rate limiting enabled
echo ========================================
echo.

echo Starting backend (4 workers)...
start "Backend" cmd /k "cd /d "%~dp0backend" && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4"
timeout /t 5 /nobreak >nul

echo Starting frontend...
start "Frontend" cmd /k "cd /d "%~dp0frontend" && npm run dev"

echo.
echo ========================================
echo   Backend: http://localhost:8000 (4 workers)
echo   Frontend: http://localhost:3000
echo   API Docs: http://localhost:8000/docs
echo   Stats: http://localhost:8000/stats
echo ========================================
echo.

timeout /t 5 /nobreak
start http://localhost:3000
