# Next Steps - Getting Your Project Running

## Step 1: Activate Virtual Environment

Open PowerShell or Command Prompt in your project directory and run:

```bash
.\venv\Scripts\Activate.ps1
```

You should see `(venv)` at the beginning of your command prompt.

## Step 2: Install Dependencies (if not already done)

```bash
pip install -r requirements.txt
```

This installs Django, scikit-learn, pandas, and other required packages.

## Step 3: Train the ML Models (CRITICAL - DO THIS FIRST!)

1. **Open Jupyter Notebook:**
   ```bash
   jupyter notebook
   ```
   This will open Jupyter in your browser.

2. **Open the training notebook:**
   - Click on `ml_model_training.ipynb` in the file browser
   
3. **Run all cells:**
   - Go to menu: `Cell` → `Run All`
   - Or press `Shift + Enter` on each cell one by one
   - Wait for all cells to complete execution

4. **Verify output files are created:**
   After training completes, you should see these files in your project root:
   - ✅ `best_disease_model.pkl`
   - ✅ `label_encoder.pkl`
   - ✅ `feature_names.pkl`

**⚠️ IMPORTANT:** The Django application will NOT work without these files!

## Step 4: Set Up Database

### Option A: Use SQLite (Easier - Automatic)

The system will automatically use SQLite if PostgreSQL is not available. No setup needed!

### Option B: Use PostgreSQL (Recommended for Production)

1. Install PostgreSQL if not installed
2. Create database:
   ```sql
   CREATE DATABASE cattle_disease_db;
   ```
3. Update `cattle_disease_system/settings.py` with your PostgreSQL credentials

## Step 5: Run Database Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

This creates all the database tables.

## Step 6: Create Superuser (Ministry Admin)

```bash
python manage.py createsuperuser
```

Follow the prompts:
- Username: (choose a username)
- Email: (optional)
- Password: (choose a strong password)

**Note:** This will be your Ministry admin account.

## Step 7: Collect Static Files

```bash
python manage.py collectstatic
```

Type `yes` when prompted. This collects all CSS and JavaScript files.

## Step 8: Run the Development Server

```bash
python manage.py runserver
```

You should see:
```
Starting development server at http://127.0.0.1:8000/
```

## Step 9: Test the System

1. **Open your browser** and go to: `http://127.0.0.1:8000/`

2. **Test as Farmer:**
   - Click "Register as Farmer"
   - Create a farmer account
   - Complete farmer profile
   - Submit a test case

3. **Test as Ministry Admin:**
   - Go to: `http://127.0.0.1:8000/admin/`
   - Login with superuser credentials
   - Or go to: `http://127.0.0.1:8000/ministry/dashboard/`

4. **Test as Vet:**
   - Click "Apply as Vet" on landing page
   - Submit vet application
   - Approve it as Ministry admin
   - Register vet login credentials

## Quick Start Commands (Copy & Paste)

```bash
# 1. Activate virtual environment
.\venv\Scripts\Activate.ps1

# 2. Install dependencies (if needed)
pip install -r requirements.txt

# 3. Train ML models (open Jupyter and run notebook)
jupyter notebook

# 4. After ML training, run migrations
python manage.py makemigrations
python manage.py migrate

# 5. Create superuser
python manage.py createsuperuser

# 6. Collect static files
python manage.py collectstatic

# 7. Run server
python manage.py runserver
```

## Troubleshooting

### Error: "ML model file not found"
**Solution:** You must train the ML models first! Run `ml_model_training.ipynb`

### Error: "No module named 'django'"
**Solution:** Activate virtual environment: `.\venv\Scripts\Activate.ps1`

### Error: "Database connection failed"
**Solution:** The system will automatically use SQLite. Check `settings.py` if using PostgreSQL.

### Error: "Static files not found"
**Solution:** Run `python manage.py collectstatic`

## What to Do Right Now

1. ✅ **First Priority:** Train ML models (Step 3)
2. ✅ **Second Priority:** Run migrations (Step 5)
3. ✅ **Third Priority:** Create superuser (Step 6)
4. ✅ **Fourth Priority:** Start server and test (Steps 7-9)

---

**Ready to start? Begin with Step 1!** 🚀
