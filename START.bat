@echo off
title Cattle Disease Prediction System
color 0A

echo.
echo ============================================================
echo    Cattle Disease Prediction System - Starting Server
echo ============================================================
echo.

cd /d "%~dp0"

echo [Step 1/3] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Could not activate virtual environment!
    pause
    exit /b 1
)

echo [Step 2/3] Running database migrations...
python manage.py migrate --noinput >nul 2>&1

echo [Step 3/3] Starting Django server...
echo.
echo ============================================================
echo    Server will open in Chrome automatically!
echo    URL: http://127.0.0.1:8000/
echo ============================================================
echo.
echo Press Ctrl+C to stop the server
echo.

python manage.py runserver

pause
