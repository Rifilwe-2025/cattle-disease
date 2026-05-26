"""
Custom password reset with OTP verification.
Flow: Enter email → Receive reset link + OTP → Click link → Enter OTP → Reset password.
"""
import logging
import random
import string
from django.shortcuts import render, redirect

logger = logging.getLogger(__name__)
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.views.generic import FormView, View
from django.contrib import messages

User = get_user_model()


def _generate_otp(length=6):
    """Generate a numeric OTP."""
    return ''.join(random.choices(string.digits, k=length))


def _get_cache_key(user_pk):
    return f'pwd_reset_otp_{user_pk}'


def password_reset_request(request):
    """
    Step 1: User enters email. We send reset link + OTP to their email.
    """
    if request.method != 'POST':
        from types import SimpleNamespace
        return render(request, 'accounts/password_reset.html', {'form': SimpleNamespace(errors={})})

    email = request.POST.get('email', '').strip().lower()
    if not email:
        messages.error(request, 'Please enter your email address.')
        return render(request, 'accounts/password_reset.html')

    users = User.objects.filter(email__iexact=email, is_active=True)
    # Always show success for security (don't reveal if email exists)
    if not users.exists():
        messages.success(
            request,
            'If an account exists with that email, we have sent password reset instructions. Please check your inbox and spam folder.'
        )
        return redirect('accounts:password_reset_done')

    from django.core.cache import cache
    timeout = getattr(settings, 'PASSWORD_RESET_OTP_TIMEOUT', 600)

    for user in users:
        token = default_token_generator.make_token(user)
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        otp = _generate_otp(6)
        cache_key = _get_cache_key(user.pk)
        cache.set(cache_key, otp, timeout=timeout)

        reset_url = request.build_absolute_uri(
            reverse('accounts:password_reset_confirm', kwargs={'uidb64': uidb64, 'token': token})
        )
        subject = 'CattleCare AI - Password Reset'
        message = f"""Hello,

You requested a password reset for your CattleCare AI account.

Your one-time verification code (OTP) is: {otp}
This code expires in 10 minutes.

Click the link below to reset your password:
{reset_url}

If you did not request this, please ignore this email. Your password will remain unchanged.

- CattleCare AI Team
"""
        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
        except Exception as e:
            logger.exception("Password reset email failed for %s: %s", user.email, e)
            if getattr(settings, 'DEBUG', False):
                messages.warning(
                    request,
                    'Email may not have been sent. Check the server console for errors (e.g. SMTP settings).'
                )

    messages.success(
        request,
        'If an account exists with that email, we have sent password reset instructions and a verification code. Please check your inbox and spam folder.'
    )
    return redirect('accounts:password_reset_done')


def password_reset_confirm_with_otp(request, uidb64, token):
    """
    Step 2 & 3: User clicks link → Enter OTP → Enter new password.
    """
    from django.core.cache import cache
    from django.contrib.auth.forms import SetPasswordForm

    # Decode user
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    validlink = user is not None and default_token_generator.check_token(user, token)
    if not validlink:
        return render(request, 'accounts/password_reset_confirm.html', {
            'validlink': False,
            'form': None,
        })

    otp_verified = request.session.get('pwd_reset_otp_verified') == uidb64

    # Step 2a: OTP form (GET or POST with wrong OTP)
    if not otp_verified:
        if request.method == 'POST':
            submitted_otp = request.POST.get('otp', '').strip()
            cache_key = _get_cache_key(user.pk)
            stored_otp = cache.get(cache_key)

            if stored_otp and submitted_otp == stored_otp:
                request.session['pwd_reset_otp_verified'] = uidb64
                cache.delete(cache_key)
                return redirect('accounts:password_reset_confirm', uidb64=uidb64, token=token)
            else:
                messages.error(request, 'Invalid or expired OTP. Please try again or request a new reset link.')
        return render(request, 'accounts/password_reset_otp.html', {
            'uidb64': uidb64,
            'token': token,
            'validlink': True,
        })

    # Step 3: Password form
    if request.method == 'POST':
        form = SetPasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            del request.session['pwd_reset_otp_verified']
            return redirect('accounts:password_reset_complete')
        else:
            return render(request, 'accounts/password_reset_confirm.html', {
                'validlink': True,
                'form': form,
            })
    else:
        form = SetPasswordForm(user)

    return render(request, 'accounts/password_reset_confirm.html', {
        'validlink': True,
        'form': form,
    })
