# Generated data migration to copy User contact info to Farmer for existing records

from django.db import migrations


def backfill_farmer_contact(apps, schema_editor):
    Farmer = apps.get_model('farmers', 'Farmer')
    for farmer in Farmer.objects.select_related('user').all():
        if not farmer.email and farmer.user.email:
            farmer.email = farmer.user.email
        if not farmer.phone_number and farmer.user.phone_number:
            farmer.phone_number = farmer.user.phone_number
        if farmer.email or farmer.phone_number:
            farmer.save()


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('farmers', '0002_add_farmer_contact_fields'),
    ]

    operations = [
        migrations.RunPython(backfill_farmer_contact, noop),
    ]
