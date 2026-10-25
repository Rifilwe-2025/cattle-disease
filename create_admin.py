"""
Create the ministry superuser for the system.

Run: python create_admin.py

The password comes from DJANGO_ADMIN_PASSWORD - it is deliberately NOT
hardcoded here. This file is committed to a public repo, so any default baked
into it would be a published credential for a publicly reachable site. There
is no fallback value on purpose: the script refuses to run rather than quietly
create an account with a password an attacker could read off GitHub.

Set it in .env (which is gitignored and loaded by settings.py) or inline:

    DJANGO_ADMIN_PASSWORD='...' python create_admin.py
"""
import os
import sys

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cattle_disease_system.settings')
django.setup()

# Read the env vars only after django.setup(), which imports settings and so
# has already loaded .env via load_dotenv.
from django.contrib.auth.password_validation import validate_password  # noqa: E402
from django.core.exceptions import ValidationError  # noqa: E402

from accounts.models import User  # noqa: E402

username = os.environ.get('DJANGO_ADMIN_USERNAME', 'admin')
email = os.environ.get('DJANGO_ADMIN_EMAIL', 'admin@ministry.gov.zw')
password = os.environ.get('DJANGO_ADMIN_PASSWORD')

if not password:
    sys.exit(
        "DJANGO_ADMIN_PASSWORD is not set.\n"
        "Set it in .env or pass it inline, then re-run:\n"
        "    DJANGO_ADMIN_PASSWORD='...' python create_admin.py"
    )

# Catch a weak password here rather than after it is already stored - the
# ministry account is a superuser on a public deployment.
try:
    validate_password(password)
except ValidationError as exc:
    sys.exit('DJANGO_ADMIN_PASSWORD is too weak:\n  ' + '\n  '.join(exc.messages))

if User.objects.filter(username=username).exists():
    # Not a failure, but don't silently reset the password of a live account
    # either - `manage.py changepassword` is the tool for that.
    print(f"User '{username}' already exists - leaving it untouched.")
    print(f"To change its password: python manage.py changepassword {username}")
else:
    User.objects.create_superuser(
        username=username,
        email=email,
        password=password,
        role='MINISTRY',
    )
    print('\n[OK] Superuser created successfully!')
    print(f'Username: {username}')
    print('Password: (the value of DJANGO_ADMIN_PASSWORD)')
    print('Role: Ministry Admin')
    print('\nYou can now login at: http://127.0.0.1:8000/admin/')
