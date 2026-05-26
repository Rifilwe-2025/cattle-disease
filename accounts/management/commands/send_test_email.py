"""
Send a test email to verify that real emails are configured.
Usage: python manage.py send_test_email rifilwe.mbengo@students.uz.ac.zw

If you see "CONSOLE backend" and no email arrives, create a .env file with
EMAIL_HOST_USER and EMAIL_HOST_PASSWORD (e.g. Gmail App Password).
"""
from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings


class Command(BaseCommand):
    help = "Send a test email to check if real emails are configured (for password reset)."

    def add_arguments(self, parser):
        parser.add_argument(
            'email',
            type=str,
            help='Email address to send the test message to (e.g. rifilwe.mbengo@students.uz.ac.zw)',
        )

    def handle(self, *args, **options):
        to_email = options['email'].strip().lower()
        backend = settings.EMAIL_BACKEND

        self.stdout.write(f'Email backend: {backend}')

        if 'console' in backend.lower():
            self.stdout.write(self.style.WARNING(
                '\nReal emails are NOT configured. Messages are only printed in this terminal.\n'
                'To send real password reset links to users:\n'
                '1. Create a file named .env in the project root (same folder as manage.py)\n'
                '2. Add these lines (use your Gmail and Gmail App Password):\n'
                '   EMAIL_HOST_USER=your_gmail@gmail.com\n'
                '   EMAIL_HOST_PASSWORD=your_16_char_app_password\n'
                '3. Restart the server (python manage.py runserver)\n'
            ))
            self.stdout.write('Sending "test" (will appear below, not in inbox)...\n')
        else:
            self.stdout.write(self.style.SUCCESS('SMTP is configured. Attempting to send real email...'))

        try:
            send_mail(
                subject='CattleCare AI - Test Email',
                message='This is a test. If you received this, password reset emails will work.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[to_email],
                fail_silently=False,
            )
            if 'console' in backend.lower():
                self.stdout.write(self.style.WARNING('(Above is what would be sent. No email was sent to inbox.)'))
            else:
                self.stdout.write(self.style.SUCCESS(f'Test email sent to {to_email}. Check inbox and spam.'))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Failed to send: {e}'))
            if 'smtp' in backend.lower():
                self.stdout.write('Check your .env: EMAIL_HOST_USER and EMAIL_HOST_PASSWORD (Gmail: use App Password).')
