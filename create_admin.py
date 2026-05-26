"""
Quick script to create a superuser for the system.
Run: python create_admin.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cattle_disease_system.settings')
django.setup()

from accounts.models import User

# Create superuser
username = 'admin'
email = 'admin@ministry.gov.zw'
password = 'admin123'

if User.objects.filter(username=username).exists():
    print(f"User '{username}' already exists!")
else:
    user = User.objects.create_superuser(
        username=username,
        email=email,
        password=password,
        role='MINISTRY'
    )
    print(f"\n[OK] Superuser created successfully!")
    print(f"Username: {username}")
    print(f"Password: {password}")
    print(f"Role: Ministry Admin")
    print(f"\nYou can now login at: http://127.0.0.1:8000/admin/")
