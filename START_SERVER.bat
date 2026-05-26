@echo off
echo ========================================
echo Starting Cattle Disease Prediction System
echo ========================================
echo.

cd /d "%~dp0"

echo [1/4] Activating virtual environment...
call venv\Scripts\activate.bat

echo [2/4] Installing/verifying dependencies...
pip install -q crispy-bootstrap5 django-crispy-forms

echo [3/4] Checking database...
python manage.py migrate --noinput

echo [4/4] Starting Django server...
echo.
echo ========================================
echo Server starting at http://127.0.0.1:8000/
echo Press Ctrl+C to stop the server
echo ========================================
echo.

python manage.py runserver

pause
