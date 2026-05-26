"""
Script to generate application IDs for existing vet applications.
Run this BEFORE creating migrations.
"""
import os
import django
import random
import string

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cattle_disease_system.settings')
django.setup()

from vets.models import VetApplication
from django.utils import timezone

def generate_application_id():
    """Generate unique application ID."""
    year = timezone.now().year
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"VET-{year}-{random_part}"

print("=" * 60)
print("GENERATING APPLICATION IDs FOR EXISTING APPLICATIONS")
print("=" * 60)
print()

# Get applications without application_id (if field exists but is empty)
try:
    applications = VetApplication.objects.all()
    print(f"Found {applications.count()} application(s)")
    print()
    
    for app in applications:
        # Check if application_id attribute exists and is empty
        if not hasattr(app, 'application_id') or not app.application_id:
            # Generate unique ID
            while True:
                app_id = generate_application_id()
                if not VetApplication.objects.filter(application_id=app_id).exists():
                    break
            
            print(f"Generated ID for {app.full_name}: {app_id}")
        else:
            print(f"Application ID already exists for {app.full_name}: {app.application_id}")
    
    print()
    print("=" * 60)
    print("Note: Migration is needed to add the application_id field.")
    print("Run 'python manage.py makemigrations' next.")
    print("=" * 60)
    
except Exception as e:
    print(f"Info: {e}")
    print()
    print("This is normal if the field doesn't exist yet.")
    print("Proceed with creating migrations.")
