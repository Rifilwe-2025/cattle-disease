# Generated manually for adding application_id field

from django.db import migrations, models
import random
import string


def generate_application_id(year=2026):
    """Generate unique application ID."""
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"VET-{year}-{random_part}"


def populate_application_ids(apps, schema_editor):
    """Populate application_id for existing applications."""
    VetApplication = apps.get_model('vets', 'VetApplication')
    
    for app in VetApplication.objects.all():
        # Generate unique ID
        while True:
            app_id = generate_application_id()
            if not VetApplication.objects.filter(application_id=app_id).exists():
                app.application_id = app_id
                app.save()
                break


class Migration(migrations.Migration):

    dependencies = [
        ('vets', '0001_initial'),
    ]

    operations = [
        # Step 1: Add field as nullable
        migrations.AddField(
            model_name='vetapplication',
            name='application_id',
            field=models.CharField(
                max_length=20,
                help_text='Unique application tracking ID (e.g., VET-2026-A1B2C3)',
                null=True,
                blank=True
            ),
        ),
        # Step 2: Populate existing records
        migrations.RunPython(populate_application_ids, migrations.RunPython.noop),
        # Step 3: Make field unique and non-nullable
        migrations.AlterField(
            model_name='vetapplication',
            name='application_id',
            field=models.CharField(
                max_length=20,
                unique=True,
                editable=False,
                help_text='Unique application tracking ID (e.g., VET-2026-A1B2C3)'
            ),
        ),
    ]
