import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cattle_disease_system.settings')
django.setup()

from ml_engine.services import predict_disease

# Test with sample data
print("=" * 60)
print("Testing predict_disease function...")
print("=" * 60)

symptoms = ['fever', 'coughing', 'dyspnea']
contextual = {
    'age_years': 3,
    'sex': 'Female',
    'breed': 'Mashona',
    'vaccinated': 'Yes',
    'herd_size': 25,
    'farming_type': 'Small-scale',
    'recent_movement': 'No',
    'season': 'Dry',
    'province': 'Harare'
}

print(f"\nSymptoms: {symptoms}")
print(f"Contextual: {contextual}")
print("\nCalling predict_disease()...")

result = predict_disease(symptoms, contextual)

print("\n" + "=" * 60)
print("RESULT:")
print("=" * 60)
print(f"Disease: {result.get('disease')}")
print(f"Confidence: {result.get('confidence')}")
if 'error' in result:
    print(f"\nERROR: {result['error']}")
else:
    print("\nSUCCESS!")
print("=" * 60)
