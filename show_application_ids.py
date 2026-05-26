"""
Script to show all vet applications with their tracking IDs.
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cattle_disease_system.settings')
django.setup()

from vets.models import VetApplication

print("=" * 80)
print("ALL VET APPLICATIONS WITH TRACKING IDs")
print("=" * 80)
print()

applications = VetApplication.objects.all().order_by('-created_at')

if not applications.exists():
    print("No applications found.")
else:
    print(f"Total Applications: {applications.count()}\n")
    
    for app in applications:
        print("-" * 80)
        print(f"APPLICATION ID: {app.application_id}")
        print(f"Name: {app.full_name}")
        print(f"Email: {app.email}")
        print(f"Phone: {app.phone_number}")
        print(f"License: {app.license_number}")
        print(f"Status: {app.get_status_display()}")
        print(f"Submitted: {app.created_at.strftime('%Y-%m-%d %H:%M')}")
        
        if app.status == 'APPROVED':
            print(f"\nTrack Application URL:")
            print(f"   http://127.0.0.1:8000/vets/track/")
            print(f"   (Vet enters: {app.application_id})")
            
            from vets.models import Vet
            if Vet.objects.filter(application=app).exists():
                print(f"Registration: COMPLETED")
            else:
                print(f"Registration: PENDING")
                print(f"\nDirect Registration URL:")
                print(f"   http://127.0.0.1:8000/vets/register/{app.application_id}/")
        
        print()

print("=" * 80)
print("\nVETS CAN TRACK THEIR APPLICATION AT:")
print("   http://127.0.0.1:8000/vets/track/")
print("\nThey just need to enter their Application ID (e.g., VET-2026-A1B2C3)")
print("=" * 80)
