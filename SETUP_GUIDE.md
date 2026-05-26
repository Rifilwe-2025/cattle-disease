# Setup Guide - Cattle Disease Prediction System

## Prerequisites

- Python 3.8 or higher
- PostgreSQL (optional, SQLite will be used as fallback)
- pip (Python package manager)
- Jupyter Notebook (for ML model training)

## Step-by-Step Setup

### 1. Clone/Extract Project

Ensure you have all project files in a directory.

### 2. Create Virtual Environment

```bash
python -m venv venv
```

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Train ML Models

1. Open Jupyter Notebook:
```bash
jupyter notebook
```

2. Open `ml_model_training.ipynb`

3. Run all cells in order

4. This will generate:
   - `best_disease_model.pkl` - The trained ML model
   - `label_encoder.pkl` - Label encoder for disease names
   - `feature_names.pkl` - List of symptom features

**Important**: These files must be in the project root directory.

### 5. Database Setup

#### Option A: PostgreSQL (Recommended)

1. Install PostgreSQL if not already installed

2. Create a database:
```sql
CREATE DATABASE cattle_disease_db;
```

3. Update `cattle_disease_system/settings.py` with your PostgreSQL credentials:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'cattle_disease_db',
        'USER': 'your_username',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

#### Option B: SQLite (Fallback)

The system will automatically use SQLite if PostgreSQL is not available. No additional setup needed.

### 6. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. Create Superuser (Ministry Admin)

```bash
python manage.py createsuperuser
```

Follow the prompts to create an admin account. This will be your Ministry admin account.

**Important**: Set the role to 'MINISTRY' or mark as superuser for full access.

### 8. Collect Static Files

```bash
python manage.py collectstatic
```

### 9. Run Development Server

```bash
python manage.py runserver
```

The application will be available at `http://127.0.0.1:8000/`

## Initial Setup Tasks

### 1. Create Ministry Admin Account

After creating the superuser, you can:
- Login to Django admin at `/admin/`
- Or use the superuser account as Ministry admin

### 2. Test the System

1. **As Farmer**:
   - Register a new farmer account
   - Complete farmer profile
   - Submit a test case

2. **As Vet**:
   - Apply for vet registration
   - Wait for Ministry approval (or approve yourself as admin)
   - Register login credentials
   - View assigned cases

3. **As Ministry**:
   - Login with superuser account
   - Approve vet applications
   - View analytics and maps

## Troubleshooting

### ML Model Files Not Found

**Error**: `ImproperlyConfigured: ML model file not found`

**Solution**: 
1. Ensure you've run the Jupyter notebook
2. Check that `.pkl` files are in the project root
3. Verify file paths in `settings.py`

### Database Connection Error

**Error**: `django.db.utils.OperationalError`

**Solution**:
1. Check PostgreSQL is running
2. Verify database credentials
3. Or let the system use SQLite (automatic fallback)

### Static Files Not Loading

**Error**: CSS/JS files not found

**Solution**:
```bash
python manage.py collectstatic
```

### Import Errors

**Error**: `ModuleNotFoundError`

**Solution**:
1. Ensure virtual environment is activated
2. Reinstall dependencies: `pip install -r requirements.txt`

## Production Deployment Notes

For production deployment:

1. Set `DEBUG = False` in `settings.py`
2. Update `ALLOWED_HOSTS`
3. Set a secure `SECRET_KEY`
4. Use a production database (PostgreSQL recommended)
5. Configure proper static file serving
6. Set up SSL/HTTPS
7. Use environment variables for sensitive data

## File Structure Verification

After setup, verify you have:

```
✓ manage.py
✓ requirements.txt
✓ ml_model_training.ipynb
✓ Training.csv
✓ Testing.csv
✓ best_disease_model.pkl
✓ label_encoder.pkl
✓ feature_names.pkl
✓ cattle_disease_system/
✓ accounts/
✓ farmers/
✓ vets/
✓ ministry/
✓ cases/
✓ ml_engine/
✓ maps/
✓ landing/
✓ templates/
✓ static/
```

## Next Steps

1. Train the ML models (if not done)
2. Create superuser account
3. Test all user roles
4. Customize UI if needed
5. Add sample data for testing

## Support

For issues or questions:
1. Check the README.md
2. Review PROJECT_STRUCTURE.md
3. Check Django documentation
4. Review error messages in console

---

**Note**: This system is designed for academic capstone presentation. Ensure all components are properly configured before presentation.
