"""
Script to get registration links for approved vet applications.
This helps Ministry admins send registration links to approved vets.
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cattle_disease_system.settings')
django.setup()

from vets.models import VetApplication, Vet

print("=" * 80)
print("VET REGISTRATION LINKS")
print("=" * 80)
print()

# Get all approved applications
approved_apps = VetApplication.objects.filter(status='APPROVED').order_by('-approved_at')

if not approved_apps.exists():
    print("No approved vet applications found.")
    print()
    print("To approve applications:")
    print("1. Go to Django Admin: http://127.0.0.1:8000/admin/")
    print("2. Navigate to Vet Applications")
    print("3. Approve pending applications")
else:
    print(f"Found {approved_apps.count()} approved application(s)\n")
    
    for app in approved_apps:
        print("-" * 80)
        print(f"Application ID: {app.id}")
        print(f"Name: {app.full_name}")
        print(f"Email: {app.email}")
        print(f"Phone: {app.phone_number}")
        print(f"License: {app.license_number}")
        print(f"Approved: {app.approved_at.strftime('%Y-%m-%d %H:%M') if app.approved_at else 'N/A'}")
        
        # Check if already registered
        if Vet.objects.filter(application=app).exists():
            vet = Vet.objects.get(application=app)
            print(f"Status: [ALREADY REGISTERED]")
            print(f"Username: {vet.user.username}")
        else:
            print(f"Status: [PENDING REGISTRATION]")
            registration_url = f"http://127.0.0.1:8000/vets/register/{app.id}/"
            print(f"\n>> SEND THIS LINK TO THE VET:")
            print(f"   {registration_url}")
            print()
            print(f">> Email Template:")
            print(f"   Subject: Complete Your Vet Registration")
            print(f"   Dear Dr. {app.full_name},")
            print(f"   ")
            print(f"   Your application has been APPROVED!")
            print(f"   ")
            print(f"   Please complete your registration by clicking the link below:")
            print(f"   {registration_url}")
            print(f"   ")
            print(f"   You'll need to create a username and password to access the system.")
            print(f"   ")
            print(f"   Regards,")
            print(f"   Ministry of Agriculture")
        
        print()

print("=" * 80)
print()
print("NEXT STEPS:")
print("   1. Copy the registration link for each approved vet")
print("   2. Send it to them via email or SMS")
print("   3. They click the link and complete registration")
print("   4. They can then login and access the vet dashboard")
print()
print("=" * 80)
