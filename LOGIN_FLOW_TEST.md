# Login Flow - Complete Test Guide

## Registration → Login → Dashboard Flow

### Step 1: Register as Farmer
1. Go to: `http://127.0.0.1:8000/`
2. Click **"Register as Farmer"**
3. Fill the form:
   - Username: `farmer1`
   - Password: `farmer123`
   - Confirm Password: `farmer123`
   - Full Name: `John Doe`
   - Phone: `+263771234567`
   - Province: Select from dropdown
   - District: `Harare Central`
   - Cattle Breed: `Brahman`
   - Number of Cattle: `50`
4. Click **"Register as Farmer"**
5. ✅ **Result:** Redirected to login page with success message

### Step 2: Login
1. On login page, enter:
   - Username: `farmer1`
   - Password: `farmer123`
2. Click **"Login"**
3. ✅ **Result:** Automatically redirected to **Farmer Dashboard**

### Step 3: Access Dashboard
- ✅ See farmer statistics
- ✅ View recent cases
- ✅ Access all farmer features

---

## What Happens Behind the Scenes

1. **Registration:**
   - Creates User account (username, password, role='FARMER')
   - Creates Farmer profile (all farm details)
   - Both saved to database
   - Redirects to login

2. **Login:**
   - Authenticates username/password
   - Checks user role
   - Redirects based on role:
     - FARMER → `/farmers/dashboard/`
     - VET → `/vets/dashboard/`
     - MINISTRY → `/ministry/dashboard/`

3. **Dashboard:**
   - Loads farmer profile
   - Shows statistics
   - Displays recent cases

---

## URLs

- **Registration:** `http://127.0.0.1:8000/farmers/register/`
- **Login:** `http://127.0.0.1:8000/accounts/login/`
- **Dashboard:** `http://127.0.0.1:8000/farmers/dashboard/`

---

## Test It Now!

1. Register a farmer
2. Login with username/password
3. You should be automatically redirected to the dashboard!
