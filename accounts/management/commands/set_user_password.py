"""
Set a user's password by email (for recovery when password reset email is not configured).
Usage:
    python manage.py set_user_password riffymbengo@gmail.com YourNewPassword123
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = "Set a user's password by email (e.g. when reset emails are not being sent)."

    def add_arguments(self, parser):
        parser.add_argument('email', type=str, help='User email (e.g. riffymbengo@gmail.com)')
        parser.add_argument('new_password', type=str, help='New password to set')

    def handle(self, *args, **options):
        email = options['email'].strip().lower()
        new_password = options['new_password']

        if not email or not new_password:
            self.stderr.write(self.style.ERROR('Email and new password are required.'))
            return

        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            self.stderr.write(self.style.ERROR(f'No user found with email: {email}'))
            return

        user.set_password(new_password)
        user.save(update_fields=['password'])
        self.stdout.write(self.style.SUCCESS(f'Password updated for user: {user.username} ({user.email})'))
        self.stdout.write('They can now log in with this email/username and the new password.')
