"""
Debug script to check user authentication.
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cattle_disease_system.settings')
django.setup()

from accounts.models import User
from django.contrib.auth import authenticate

print("=" * 60)
print("DATABASE CHECK - Users in System")
print("=" * 60)

# List all users
users = User.objects.all()
print(f"\nTotal users: {users.count()}")
print("\nUser Details:")
for user in users:
    print(f"\n  Username: {user.username}")
    print(f"  Role: {user.role}")
    print(f"  Active: {user.is_active}")
    print(f"  Phone: {user.phone_number}")
    print(f"  Has usable password: {user.has_usable_password()}")
    
    # Check if farmer profile exists
    if user.role == 'FARMER':
        try:
            farmer = user.farmer_profile
            print(f"  Farmer Name: {farmer.full_name}")
            print(f"  Province: {farmer.province}")
        except:
            print(f"  [WARNING] No farmer profile found!")

print("\n" + "=" * 60)
print("AUTHENTICATION TEST")
print("=" * 60)

# Test authentication with the most recent user
if users.exists():
    latest_user = users.order_by('-created_at').first()
    print(f"\nTesting authentication for: {latest_user.username}")
    print("Note: You'll need to know the password you used during registration")
    
    # Try common test passwords
    test_passwords = ['test1234', 'password123', 'farmer123']
    
    print("\nTrying common test passwords...")
    for pwd in test_passwords:
        result = authenticate(username=latest_user.username, password=pwd)
        if result:
            print(f"  [SUCCESS] Password '{pwd}' works!")
            break
        else:
            print(f"  [FAILED] Password '{pwd}' doesn't work")
    
    # Manual check
    print("\n" + "-" * 60)
    print("To test your actual password, run:")
    print(f"  python -c \"import django; django.setup(); from django.contrib.auth import authenticate; print(authenticate(username='{latest_user.username}', password='YOUR_PASSWORD'))\"")
else:
    print("\n[WARNING] No users found in database!")
    print("Please register a farmer first at: http://127.0.0.1:8000/farmers/register/")

print("\n" + "=" * 60)
