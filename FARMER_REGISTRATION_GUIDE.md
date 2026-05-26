# Farmer Registration Flow - Complete Guide

## Registration Process

### Step 1: Access Registration Page
- Go to landing page: `http://127.0.0.1:8000/`
- Click **"Register as Farmer"** button
- OR go directly to: `http://127.0.0.1:8000/farmers/register/`

### Step 2: Fill Registration Form

The form has **4 sections**:

#### 1. Account Information
- **Username** (required) - Choose a unique username
- **Password** (required) - Minimum 8 characters
- **Confirm Password** (required) - Must match password

#### 2. Personal Information
- **Full Name** (required)
- **Phone Number** (required) - Format: +263XXXXXXXXX

#### 3. Location Information
- **Province** (required) - Select from dropdown
- **District** (required)
- **Latitude** (optional) - GPS coordinate
- **Longitude** (optional) - GPS coordinate
- **Get GPS Location** button - Automatically captures coordinates

#### 4. Farm Information
- **Cattle Breed** (required) - e.g., Brahman, Angus
- **Number of Cattle** (required) - Minimum 1

### Step 3: Submit Registration

- Click **"Register as Farmer"** button
- System creates:
  - ✅ User account (saved to database)
  - ✅ Farmer profile (saved to database)
- Redirects to **Login Page**

### Step 4: Login

- Enter your **Username** and **Password**
- Click **Login**
- Redirected to **Farmer Dashboard**

---

## Database Storage

All data is saved to **PostgreSQL** database:

### User Table (accounts_user)
- username
- password (hashed)
- role = 'FARMER'
- phone_number
- created_at

### Farmer Table (farmers_farmer)
- user (foreign key to User)
- full_name
- province
- district
- latitude
- longitude
- cattle_breed
- number_of_cattle
- farming_type
- created_at

---

## PostgreSQL Setup

### If PostgreSQL is not configured:

1. **Install PostgreSQL** (if not installed)
2. **Create database:**
   ```sql
   CREATE DATABASE cattle_disease_db;
   ```
3. **Update settings.py:**
   - Change `PASSWORD` to your PostgreSQL password
4. **Run migrations:**
   ```powershell
   python manage.py migrate
   ```

### If PostgreSQL fails:
- System automatically uses **SQLite** as fallback
- All data still saved correctly

---

## Testing the Flow

1. **Start server:**
   ```powershell
   python manage.py runserver
   ```

2. **Open browser:** `http://127.0.0.1:8000/`

3. **Click "Register as Farmer"**

4. **Fill the form** with test data:
   - Username: `farmer1`
   - Password: `farmer123`
   - Full Name: `John Doe`
   - Phone: `+263771234567`
   - Province: `Harare`
   - District: `Harare Central`
   - Cattle Breed: `Brahman`
   - Number: `50`

5. **Submit** → Redirects to login

6. **Login** with username and password

7. **Access Dashboard**

---

## Verification

After registration, verify in database:

```sql
-- Check user
SELECT username, role FROM accounts_user WHERE role = 'FARMER';

-- Check farmer profile
SELECT full_name, province, cattle_breed FROM farmers_farmer;
```

Or use Django admin:
- Go to: `http://127.0.0.1:8000/admin/`
- Login with admin credentials
- Check "Users" and "Farmers" sections
