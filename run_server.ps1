# PowerShell script to start server and open Chrome
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting Cattle Disease Prediction System" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Navigate to project directory
Set-Location $PSScriptRoot

# Activate virtual environment
Write-Host "[1/4] Activating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

# Run migrations (silently)
Write-Host "[2/4] Checking database..." -ForegroundColor Yellow
python manage.py migrate --noinput 2>&1 | Out-Null

# Start server in background
Write-Host "[3/4] Starting Django server..." -ForegroundColor Yellow
Start-Process python -ArgumentList "manage.py", "runserver" -WindowStyle Hidden

# Wait for server to start
Write-Host "[4/4] Waiting for server to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

# Open Chrome
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Opening Chrome browser..." -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

$url = "http://127.0.0.1:8000/"
Start-Process "chrome.exe" -ArgumentList $url

Write-Host "Server is running at: $url" -ForegroundColor Green
Write-Host "Browser opened automatically!" -ForegroundColor Green
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Keep script running
python manage.py runserver
