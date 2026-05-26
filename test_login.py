"""
Quick script to test login functionality.
Run: python test_login.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cattle_disease_system.settings')
django.setup()

from django.contrib.auth import authenticate
from accounts.models import User
from farmers.models import Farmer

print("=" * 60)
print("Testing Login Functionality")
print("=" * 60)

# Get all farmer users
farmer_users = User.objects.filter(role='FARMER')

if farmer_users.exists():
    print(f"\nFound {farmer_users.count()} farmer user(s):\n")
    for user in farmer_users:
        print(f"Username: {user.username}")
        print(f"Role: {user.role}")
        print(f"Is Active: {user.is_active}")
        print(f"Is Farmer: {user.is_farmer()}")
        
        # Check if farmer profile exists
        try:
            farmer = Farmer.objects.get(user=user)
            print(f"Farmer Profile: {farmer.full_name}")
        except Farmer.DoesNotExist:
            print("⚠️  WARNING: No farmer profile found!")
        
        print("-" * 60)
else:
    print("\nNo farmer users found. Please register a farmer first.")

print("\n" + "=" * 60)
print("To test login, try:")
print("1. Register a new farmer")
print("2. Use the username and password you entered")
print("3. Login should redirect to farmer dashboard")
print("=" * 60)
