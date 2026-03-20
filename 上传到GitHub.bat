@echo off
chcp 437 >nul
title Upload to GitHub
cd /d "%~dp0"

echo ========================================
echo       Upload to GitHub
echo ========================================
echo.

echo [Step 1] Enter your Personal Access Token:
echo (Get token from: https://github.com/settings/tokens)
set /p TOKEN="Token: "

echo.
echo [Step 2] Initializing Git...
git init
git config user.email "1825073145@qq.com"
git config user.name "cccyyywqq"

echo [Step 3] Adding all files...
git add .

echo [Step 4] Committing...
git commit -m "feat: optimize backend with caching, rate limiting, retry mechanism; add Docker deployment"

echo [Step 5] Setting remote...
git remote remove origin 2>nul
git remote add origin https://%TOKEN%@github.com/cccyyywqq/paper-polish.git
git branch -M main

echo [Step 6] Pushing to GitHub...
git push -u origin main --force

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo       SUCCESS!
    echo ========================================
    echo.
    echo Repository: https://github.com/cccyyywqq/paper-polish
    echo.
    start https://github.com/cccyyywqq/paper-polish
) else (
    echo.
    echo [ERROR] Push failed!
    echo Please check:
    echo 1. Token is valid
    echo 2. Repository exists on GitHub
    echo 3. Network connection is stable
)

echo.
pause
