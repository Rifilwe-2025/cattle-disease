# Quick Start Commands - Copy & Paste These

## Step 1: Navigate to Project Directory
```powershell
cd "C:\Users\Riflwe\Desktop\Early Disease Prediction For Cattle"
```

## Step 2: Activate Virtual Environment
```powershell
.\venv\Scripts\Activate.ps1
```

**OR if PowerShell gives error, use:**
```cmd
venv\Scripts\activate.bat
```

## Step 3: Install Missing Package (if needed)
```powershell
pip install crispy-bootstrap5
```

## Step 4: Verify Installation
```powershell
python -c "import crispy_bootstrap5; print('OK - Package installed')"
```

## Step 5: Run Migrations (if needed)
```powershell
python manage.py migrate
```

## Step 6: Start the Server
```powershell
python manage.py runserver
```

---

## OR Use the Batch File (Easiest)

Just double-click: **START_SERVER.bat**

Or run in terminal:
```cmd
START_SERVER.bat
```

---

## If You Still Get Errors

### Check Virtual Environment is Activated
You should see `(venv)` at the start of your command prompt:
```
(venv) C:\Users\Riflwe\Desktop\Early Disease Prediction For Cattle>
```

### If NOT activated, run:
```powershell
.\venv\Scripts\Activate.ps1
```

### Verify Python is using venv:
```powershell
python -c "import sys; print(sys.executable)"
```
Should show path to venv\Scripts\python.exe

### Reinstall crispy-bootstrap5:
```powershell
pip uninstall crispy-bootstrap5 -y
pip install crispy-bootstrap5
```

---

## Complete Command Sequence (Copy All)

```powershell
cd "C:\Users\Riflwe\Desktop\Early Disease Prediction For Cattle"
.\venv\Scripts\Activate.ps1
pip install crispy-bootstrap5
python manage.py migrate
python manage.py runserver
```
