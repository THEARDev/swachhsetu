@echo off
title SwachhSetu — Dev Server
color 0A

echo.
echo =====================================================
echo   🌿  SwachhSetu — Waste Management System
echo =====================================================
echo.

REM Step 1: Check venv exists
if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] venv nahi mila. Pehle setup chalao:
    echo     python -m venv venv
    pause
    exit /b 1
)

REM Step 2: Activate venv
call venv\Scripts\activate.bat

REM Step 3: Go to backend
cd backend

REM Step 4: Run Flask
echo [INFO] Starting backend on http://localhost:5000
echo [INFO] Browser will open automatically...
echo.
echo Press CTRL+C to stop the server.
echo.

python app.py

pause