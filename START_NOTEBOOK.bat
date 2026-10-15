@echo off
title ML Model Training Notebook
color 0B

echo.
echo ============================================================
echo    Opening ML Model Notebook in your browser
echo ============================================================
echo.

cd /d "%~dp0"

echo [Step 1/2] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Could not activate virtual environment!
    echo Run: python -m venv venv
    pause
    exit /b 1
)

echo [Step 2/2] Starting Jupyter Notebook...
echo.
echo Your browser will open automatically.
echo To stop: close this window or press Ctrl+C twice.
echo.

python -m jupyter notebook ml_model_training.ipynb

pause
