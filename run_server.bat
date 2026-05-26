@echo off
echo ========================================
echo Starting Cattle Disease Prediction System
echo ========================================
echo.

cd /d "%~dp0"

echo [1/4] Activating virtual environment...
call venv\Scripts\activate.bat

echo [2/4] Checking database...
python manage.py migrate --noinput >nul 2>&1

echo [3/4] Starting Django server...
start /B python manage.py runserver

echo [4/4] Waiting for server to start...
timeout /t 3 /nobreak >nul

echo.
echo ========================================
echo Opening browser...
echo ========================================
echo.

start "" "http://127.0.0.1:8000/"

echo Server is running at http://127.0.0.1:8000/
echo Press Ctrl+C in this window to stop the server
echo.
pause
