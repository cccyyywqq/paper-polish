@echo off
title Paper Polish Tool
color 0A

echo ========================================
echo       Paper Polish Tool
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
echo Starting services...
start "Backend" cmd /k "cd /d "%~dp0backend" && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
timeout /t 3 /nobreak >nul
start "Frontend" cmd /k "cd /d "%~dp0frontend" && npm run dev"

echo.
echo ========================================
echo   Backend: http://localhost:8000
echo   Frontend: http://localhost:3000
echo   API Docs: http://localhost:8000/docs
echo ========================================
echo.

timeout /t 5 /nobreak
start http://localhost:3000
