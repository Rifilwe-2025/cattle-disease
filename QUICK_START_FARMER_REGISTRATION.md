# Quick Start - Farmer Registration

## ✅ Everything is Ready!

The farmer registration system is fully implemented with:
- ✅ Complete registration form (all required fields)
- ✅ User account creation
- ✅ Farmer profile creation
- ✅ PostgreSQL database support
- ✅ Automatic redirect to login after registration
- ✅ Beautiful, modern UI

---

## How to Run

### Option 1: Quick Start (Recommended)

**Just run:**
```powershell
python manage.py runserver
```

Then open: `http://127.0.0.1:8000/`

### Option 2: Use Batch File

**Double-click:** `START.bat`

---

## Test Farmer Registration

1. **Open browser:** `http://127.0.0.1:8000/`
2. **Click:** "Register as Farmer" button
3. **Fill the form:**
   - Username: `farmer1`
   - Password: `farmer123`
   - Confirm Password: `farmer123`
   - Full Name: `John Doe`
   - Phone: `+263771234567`
   - Province: Select from dropdown
   - District: `Harare Central`
   - Cattle Breed: `Brahman`
   - Number of Cattle: `50`
4. **Click:** "Register as Farmer"
5. **Result:** Redirected to login page
6. **Login** with username and password
7. **Access** farmer dashboard

---

## PostgreSQL Setup (If Needed)

### If you see database connection error:

1. **Install PostgreSQL** (if not installed)
2. **Create database:**
   ```sql
   CREATE DATABASE cattle_disease_db;
   ```
3. **Update `settings.py` line 95:**
   ```python
   'PASSWORD': 'your_postgres_password',
   ```
4. **Run migrations:**
   ```powershell
   python manage.py migrate
   ```

### Or use SQLite (easier):

Edit `cattle_disease_system/settings.py` and comment out PostgreSQL, uncomment SQLite section.

---

## Registration Form Fields

### Required Fields:
- ✅ Username
- ✅ Password
- ✅ Confirm Password
- ✅ Full Name
- ✅ Phone Number
- ✅ Province
- ✅ District
- ✅ Cattle Breed
- ✅ Number of Cattle

### Optional Fields:
- Latitude (GPS)
- Longitude (GPS)

---

## Data Storage

All data is saved to database:
- **User account** → `accounts_user` table
- **Farmer profile** → `farmers_farmer` table

Both are linked together and saved when you register!

---

## Ready to Test! 🚀

Just run the server and try registering a farmer!
