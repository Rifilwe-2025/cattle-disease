# Login Troubleshooting Guide

## Issue: Cannot Login After Registration

If you registered successfully but cannot login, follow these steps:

---

## Step 1: Verify Your Account Exists

Run this command to see all users in the database:

```bash
python debug_login.py
```

This will show:
- All usernames in the system
- Their roles (FARMER, VET, MINISTRY)
- Whether they have a valid password set
- Their farmer profile information

**Current users in your database:**
- `taku` (FARMER) - Takura chimuti
- `Ree` (FARMER) - Riflwe Mbengo  
- `admin` (MINISTRY)

---

## Step 2: Test Your Specific Login Credentials

Run this interactive script to test your exact username and password:

```bash
python test_specific_login.py
```

Enter your username and password when prompted. This will tell you:
- If the username exists
- If the password is correct
- What might be wrong

---

## Step 3: Try Logging In

1. Go to: http://127.0.0.1:8000/accounts/login/

2. Enter your **exact** username (case-sensitive)

3. Enter your **exact** password (case-sensitive)

4. Click "Login"

5. **Check the terminal** where `python manage.py runserver` is running. You should see DEBUG messages like:

```
[DEBUG LOGIN] Attempting login:
  Username: your_username
  Password length: 8
  User exists: YES
  User role: FARMER
  User active: True
  Has usable password: True
  Authentication result: <User: your_username (Farmer)>
  Login successful! Role: FARMER
  Redirecting to: accounts:redirect_after_login

[DEBUG REDIRECT] Redirecting user:
  Username: your_username
  Role: FARMER
  Is farmer: True
  Redirecting to: farmers:dashboard
```

---

## Common Issues & Solutions

### Issue 1: "Invalid username. This username does not exist."
**Solution:** 
- Double-check your username spelling
- Usernames are case-sensitive
- Run `python debug_login.py` to see all usernames

### Issue 2: "Invalid password. Please check your password and try again."
**Solution:**
- Make sure you're entering the exact password you used during registration
- Passwords are case-sensitive
- No extra spaces before or after
- Minimum 8 characters required during registration

### Issue 3: Login seems to work but stays on login page
**Solution:**
- Check the terminal output for debug messages
- Look for any errors about Farmer profile not found
- The user might not have a linked Farmer profile

### Issue 4: "Access denied. Farmers only."
**Solution:**
- Your user account exists but doesn't have the FARMER role
- Run `python debug_login.py` to check your role
- Contact admin to fix your role

---

## Step 4: Register a Fresh Test Account

If you're still having issues, try registering a brand new account:

1. Go to: http://127.0.0.1:8000/farmers/register/

2. Use these test credentials:
   - **Username:** `testfarmer`
   - **Password:** `test1234`
   - **Full Name:** `Test Farmer`
   - **Phone:** `0780000000`
   - **Province:** Any province
   - **District:** Any district
   - **Cattle Breed:** `Brahman`
   - **Number of Cattle:** `10`

3. After successful registration, you'll be redirected to the login page

4. Login with:
   - **Username:** `testfarmer`
   - **Password:** `test1234`

5. You should be redirected to the farmer dashboard

---

## Step 5: Check Debug Output

The login system now has extensive debugging enabled. When you try to login, watch the terminal where `python manage.py runserver` is running.

You'll see detailed output showing:
- What username was entered
- If the user exists in the database
- If authentication succeeded or failed
- What role the user has
- Where the system is trying to redirect

This will help pinpoint exactly where the login process is failing.

---

## Need More Help?

If you've followed all these steps and still can't login:

1. Copy the **complete terminal output** from when you try to login (including all DEBUG messages)

2. Run `python debug_login.py` and copy the output

3. Share both outputs for further diagnosis

---

## Technical Details

**What was changed to fix login issues:**

1. **Simplified LoginForm** (`accounts/forms.py`):
   - Changed from `AuthenticationForm` to a simple `forms.Form`
   - This ensures better compatibility with the custom User model

2. **Enhanced debugging** (`accounts/views.py`):
   - Added detailed console output for every login attempt
   - Shows exactly what's being checked at each step
   - Helps identify authentication failures immediately

3. **Better error messages**:
   - Specific messages for "username not found" vs "wrong password"
   - More helpful guidance for users

4. **Debug scripts**:
   - `debug_login.py` - Lists all users and their status
   - `test_specific_login.py` - Tests specific credentials interactively

---

## Success Indicators

When login works correctly, you'll see:

1. ✅ Terminal shows `[DEBUG LOGIN] ... Login successful!`
2. ✅ Terminal shows `[DEBUG REDIRECT] ... Redirecting to: farmers:dashboard`
3. ✅ Browser redirects to `http://127.0.0.1:8000/farmers/dashboard/`
4. ✅ You see the Farmer Dashboard with your name
5. ✅ Green success message: "Welcome back, Your Name!"

---

## Database Information

**Database:** SQLite (db.sqlite3)  
**Custom User Model:** `accounts.User`  
**Farmer Profile Model:** `farmers.Farmer`

Each farmer has:
- A User account (for authentication)
- A Farmer profile (for farmer-specific data)

Both must be properly linked for login to work correctly.
