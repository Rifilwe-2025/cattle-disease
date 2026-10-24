"""
Account email: the password-reset link and its one-time code.

Separate from the view for the same reason as cases.notifications - the
message is rendered while a request is in scope, and only finished strings are
handed to the sending thread.
"""
import logging

from django.utils.html import escape

from core.mailer import send_email

logger = logging.getLogger(__name__)


def send_password_reset_email(*, to_email, display_name, reset_url, otp,
                              expires_minutes=10):
    """
    Send one user their reset link and OTP.

    Both travel in the same message by design: the link proves the mailbox was
    reachable and the OTP proves it was *read*, so a link leaked from a browser
    history or a shared-device back button is not on its own enough to take an
    account over.

    Returns True if the message was queued.
    """
    greeting = display_name.strip() if display_name and display_name.strip() else 'there'

    body = '\n'.join([
        f'Hello {greeting},',
        '',
        'You asked to reset the password on your CattleCare AI account.',
        '',
        f'Your one-time verification code is:  {otp}',
        f'It expires in {expires_minutes} minutes.',
        '',
        'Open this link, enter the code, then choose a new password:',
        reset_url,
        '',
        'If you did not ask for this, you can ignore this email - your password '
        'will not change, and nobody can reset it without the code above.',
        '',
        '- CattleCare AI',
    ])

    return send_email(
        subject='CattleCare AI - Password Reset',
        body=body,
        recipients=[to_email],
        html_body=_reset_html(
            greeting=greeting, reset_url=reset_url, otp=otp,
            expires_minutes=expires_minutes,
        ),
    )


def _reset_html(*, greeting, reset_url, otp, expires_minutes):
    """
    HTML alternative for the reset email.

    Nested tables and inline styles, for the reasons set out in
    cases.notifications._assignment_html. The code itself is set in a monospace
    face at wide letter-spacing because its whole job is to be transcribed by
    hand into another window, and a proportional font makes 0/O and 1/l a
    guess.
    """
    return f"""<!DOCTYPE html>
<html><body style="margin:0;padding:24px 12px;background:#f3f4f6;
  font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Arial,sans-serif">
<table role="presentation" cellpadding="0" cellspacing="0" border="0"
       style="max-width:600px;margin:0 auto;background:#ffffff;border-radius:12px;
              overflow:hidden">
  <tr><td style="height:4px;background:#2d5a4a"></td></tr>
  <tr><td style="padding:32px">
    <p style="margin:0 0 4px;color:#2d5a4a;font-size:12px;font-weight:700;
              text-transform:uppercase;letter-spacing:.08em">Password reset</p>
    <h1 style="margin:0 0 20px;color:#111827;font-size:22px;font-weight:700">
      Choose a new password</h1>
    <p style="margin:0 0 24px;color:#374151;font-size:15px;line-height:1.6">
      Hello {escape(greeting)}, you asked to reset the password on your
      CattleCare AI account.</p>

    <table role="presentation" cellpadding="0" cellspacing="0" border="0"
           style="width:100%;margin:0 0 8px;background:#f9fafb;border-radius:8px">
      <tr><td style="padding:20px;text-align:center">
        <p style="margin:0 0 8px;color:#6b7280;font-size:13px;
                  text-transform:uppercase;letter-spacing:.04em">
          Your verification code</p>
        <p style="margin:0;color:#111827;font-size:32px;font-weight:700;
                  letter-spacing:.22em;font-family:'SFMono-Regular',Consolas,
                  'Liberation Mono',Menlo,monospace">{escape(otp)}</p>
      </td></tr>
    </table>
    <p style="margin:0 0 24px;color:#9ca3af;font-size:13px;text-align:center">
      Expires in {expires_minutes} minutes.</p>

    <table role="presentation" cellpadding="0" cellspacing="0" border="0"
           style="margin:0 0 24px">
      <tr><td style="background:#2d5a4a;border-radius:8px">
        <a href="{escape(reset_url)}"
           style="display:inline-block;padding:13px 26px;color:#ffffff;
                  font-size:15px;font-weight:600;text-decoration:none">
          Reset my password</a>
      </td></tr>
    </table>

    <p style="margin:0 0 8px;color:#6b7280;font-size:13px;line-height:1.6">
      If the button does not work, copy this link into your browser:</p>
    <p style="margin:0 0 24px;color:#2d5a4a;font-size:12px;word-break:break-all">
      {escape(reset_url)}</p>

    <p style="margin:0;color:#6b7280;font-size:13px;line-height:1.6">
      If you did not ask for this you can ignore this email - your password will
      not change, and nobody can reset it without the code above.</p>
  </td></tr>
  <tr><td style="padding:16px 32px;background:#f9fafb;border-top:1px solid #e5e7eb">
    <p style="margin:0;color:#9ca3af;font-size:12px">
      CattleCare AI &middot; Early Disease Prediction for Cattle</p>
  </td></tr>
</table>
</body></html>"""
