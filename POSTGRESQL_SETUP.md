# PostgreSQL Database Setup Guide

## Step 1: Install PostgreSQL

If you don't have PostgreSQL installed:
1. Download from: https://www.postgresql.org/download/windows/
2. Install with default settings
3. Remember the password you set for the 'postgres' user

## Step 2: Create Database

Open PostgreSQL Command Line or pgAdmin and run:

```sql
CREATE DATABASE cattle_disease_db;
```

## Step 3: Update Settings

Edit `cattle_disease_system/settings.py` and update the database password:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'cattle_disease_db',
        'USER': 'postgres',
        'PASSWORD': 'YOUR_POSTGRES_PASSWORD',  # Change this!
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

## Step 4: Run Migrations

```powershell
.\venv\Scripts\Activate.ps1
python manage.py migrate
```

## Step 5: Verify Connection

The system will automatically fall back to SQLite if PostgreSQL is not available.

## Troubleshooting

### Error: "password authentication failed"
- Check your PostgreSQL password in settings.py
- Make sure PostgreSQL service is running

### Error: "database does not exist"
- Create the database: `CREATE DATABASE cattle_disease_db;`

### Error: "connection refused"
- Make sure PostgreSQL service is running
- Check if port 5432 is correct
