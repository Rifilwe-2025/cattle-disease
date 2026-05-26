# How to Fix Virtual Environment Issues

## The Problem

You're seeing this message because:
- VS Code or your terminal is using **global Python** instead of your **venv Python**
- Packages are being installed globally, causing conflicts

## Solution: Always Use Your Virtual Environment

### Method 1: Activate venv in Terminal (Recommended)

**Every time you open a terminal, run this first:**

```powershell
cd "C:\Users\Riflwe\Desktop\Early Disease Prediction For Cattle"
.\venv\Scripts\Activate.ps1
```

You should see `(venv)` appear at the start of your prompt.

### Method 2: Configure VS Code to Auto-Use venv

1. **Press `Ctrl+Shift+P`**
2. **Type:** `Python: Select Interpreter`
3. **Choose:** `.\venv\Scripts\python.exe`

VS Code will now always use your venv!

### Method 3: Use the Batch File

I created `START_SERVER.bat` - it automatically activates venv and starts the server.

Just double-click it or run:
```cmd
START_SERVER.bat
```

## Verify venv is Active

Run this command:
```powershell
python -c "import sys; print(sys.executable)"
```

**Should show:**
```
C:\Users\Riflwe\Desktop\Early Disease Prediction For Cattle\venv\Scripts\python.exe
```

**If it shows something else (like `C:\Python\...`), venv is NOT active!**

## Complete Setup Commands

Copy and paste these in order:

```powershell
# 1. Go to project folder
cd "C:\Users\Riflwe\Desktop\Early Disease Prediction For Cattle"

# 2. Activate virtual environment
.\venv\Scripts\Activate.ps1

# 3. Verify it's active (should show venv path)
python -c "import sys; print('Python:', sys.executable)"

# 4. Install/verify packages
pip install crispy-bootstrap5 django-crispy-forms

# 5. Verify package is installed
python -c "import crispy_bootstrap5; print('SUCCESS!')"

# 6. Run Django
python manage.py runserver
```

## If PowerShell Gives Execution Policy Error

Run this once:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then activate venv again:
```powershell
.\venv\Scripts\Activate.ps1
```

## Summary

**The key is: ALWAYS activate your venv before running Python commands!**

✅ **DO THIS:**
```powershell
.\venv\Scripts\Activate.ps1
python manage.py runserver
```

❌ **DON'T DO THIS:**
```powershell
python manage.py runserver  # Without activating venv first!
```
