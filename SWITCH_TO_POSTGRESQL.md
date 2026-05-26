# How to Switch to PostgreSQL (When Ready)

## Current Setup
✅ **Using SQLite** - Works immediately, no setup needed

## To Switch to PostgreSQL Later

### Step 1: Install PostgreSQL
Download from: https://www.postgresql.org/download/windows/

### Step 2: Create Database
Open PostgreSQL Command Line (psql) or pgAdmin and run:
```sql
CREATE DATABASE cattle_disease_db;
```

### Step 3: Update settings.py

Edit `cattle_disease_system/settings.py`:

**Comment out SQLite (lines 82-87):**
```python
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }
```

**Uncomment PostgreSQL (lines 89-97) and update password:**
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'cattle_disease_db',
        'USER': 'postgres',
        'PASSWORD': 'your_actual_password',  # Change this!
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### Step 4: Run Migrations
```powershell
python manage.py migrate
```

---

## For Now: SQLite Works Perfectly!

SQLite is fine for development and testing. You can switch to PostgreSQL later for production.
