"""
Test authentication for a specific username and password.
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cattle_disease_system.settings')
django.setup()

from django.contrib.auth import authenticate
from accounts.models import User

print("=" * 60)
print("LOGIN AUTHENTICATION TEST")
print("=" * 60)

# Get username from user
username = input("\nEnter your username: ")
password = input("Enter your password: ")

print("\n" + "-" * 60)
print(f"Testing authentication for: {username}")
print("-" * 60)

# Check if user exists
try:
    user_obj = User.objects.get(username=username)
    print(f"\n[OK] User found in database")
    print(f"  Username: {user_obj.username}")
    print(f"  Role: {user_obj.role}")
    print(f"  Active: {user_obj.is_active}")
    print(f"  Has usable password: {user_obj.has_usable_password()}")
    
    if user_obj.role == 'FARMER':
        try:
            farmer = user_obj.farmer_profile
            print(f"  Farmer Name: {farmer.full_name}")
        except:
            print(f"  [WARNING] No farmer profile linked!")
    
except User.DoesNotExist:
    print(f"\n[ERROR] User '{username}' does not exist!")
    print("Please check your username and try again.")
    exit(1)

# Try authentication
print("\n" + "-" * 60)
print("Testing authentication...")
print("-" * 60)

result = authenticate(username=username, password=password)

if result:
    print(f"\n[SUCCESS] Authentication successful!")
    print(f"  Authenticated user: {result.username}")
    print(f"  Role: {result.role}")
    print(f"\nYou should be able to login with these credentials.")
else:
    print(f"\n[FAILED] Authentication failed!")
    print(f"  The password is incorrect.")
    print(f"\nPlease double-check your password.")
    print(f"Password is case-sensitive and must match exactly.")

print("\n" + "=" * 60)
