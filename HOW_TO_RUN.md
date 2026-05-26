# How to Run the System - Opens Chrome Automatically

## Method 1: Use the Batch File (Easiest) ⭐

**Just double-click:** `START.bat`

This will:
- ✅ Activate virtual environment
- ✅ Run migrations
- ✅ Start Django server
- ✅ Open Chrome automatically

---

## Method 2: Run Command Manually

### Step 1: Open Terminal/PowerShell

### Step 2: Navigate to Project
```powershell
cd "C:\Users\Riflwe\Desktop\Early Disease Prediction For Cattle"
```

### Step 3: Activate Virtual Environment
```powershell
.\venv\Scripts\Activate.ps1
```

### Step 4: Run Server (Opens Chrome Automatically)
```powershell
python manage.py runserver
```

**The browser will open automatically after 2 seconds!**

---

## What Happens When You Run `python manage.py runserver`

1. ✅ Server starts at `http://127.0.0.1:8000/`
2. ✅ Chrome opens automatically after 2 seconds
3. ✅ You see the beautiful landing page

---

## If Chrome Doesn't Open Automatically

### Option 1: Use the Batch File
Double-click `START.bat` - it will open Chrome for you.

### Option 2: Open Manually
After server starts, open Chrome and go to:
```
http://127.0.0.1:8000/
```

---

## UI Features

The system has a modern, professional design with:
- ✅ Beautiful gradient hero section
- ✅ Smooth animations and hover effects
- ✅ Responsive design (works on mobile too)
- ✅ Professional color scheme
- ✅ Clean, modern cards and buttons
- ✅ Font Awesome icons
- ✅ Bootstrap 5 styling

---

## Quick Reference

**Easiest way:**
```
Double-click START.bat
```

**Manual way:**
```powershell
.\venv\Scripts\Activate.ps1
python manage.py runserver
```

---

## Troubleshooting

### Server won't start?
1. Make sure venv is activated (see `(venv)` in prompt)
2. Run: `pip install -r requirements.txt`

### Chrome doesn't open?
1. Use `START.bat` instead
2. Or manually open: `http://127.0.0.1:8000/`

### Port already in use?
Change port: `python manage.py runserver 8001`
