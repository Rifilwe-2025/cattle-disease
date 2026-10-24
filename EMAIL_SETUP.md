# Email setup

The system sends two kinds of email:

- **Password reset** — the reset link and a 6-digit one-time code, to the
  address the user registered with.
- **Vet assignment** — when a farmer picks a vet for a case, that vet is
  emailed the case details, the farmer's contact details, and a link straight
  to the case. Reply-To is the farmer, so the vet can simply hit reply.

Both go through `core.mailer.send_email`, which renders the message in the
request and transmits it on a background thread, so a slow mail server never
holds up a page. A send that fails is logged, never raised — the case is
already saved and the reset token is already valid.

---

## The one thing to know first: Render blocks Gmail

**Gmail SMTP cannot work from the deployed site, and no amount of
configuration will change that.**

Since 26 September 2025, Render's **free** web services block outbound traffic
on SMTP ports **25, 465 and 587**. Gmail only offers 587 and 465, so both are
blocked. Measured against this service, the failure looks like:

```
ERROR core.mailer Email FAILED: 'CattleCare AI - Password Reset' -> ...
OSError: [Errno 101] Network is unreachable
```

That is the platform refusing the connection, not a credentials problem. The
same Gmail settings send fine from a laptop, which is what makes this so
confusing to diagnose — and is why the error is now logged loudly.

Port **2525 is not blocked**, and that is the way out on the free plan. This
was verified against the live service: pointing `EMAIL_HOST` at
`smtp-relay.brevo.com:2525` got all the way to `535 Authentication failed`,
meaning the TCP connection, STARTTLS and SMTP conversation all succeeded and
only the credentials were wrong.

| Route | Port | Works on Render free? |
| --- | --- | --- |
| Gmail | 587 / 465 | **No** — blocked by Render |
| Brevo / SendGrid / Mailgun relay | 2525 | **Yes** |
| Any provider's HTTP API | 443 | Yes, but needs a custom email backend |
| Gmail, on a **paid** Render instance | 587 | Yes — paid plans unblock 587/465 |

---

## Setting it up with Brevo (free, recommended)

Brevo's free tier covers roughly 300 emails a day, which is far more than a
prototype needs.

1. Create a free account at <https://www.brevo.com>.
2. Verify the address you want mail to come **from** (Senders & IPs →
   Senders). Brevo will not send on behalf of an unverified sender.
3. Go to **SMTP & API → SMTP**. Note the **login** (an email address or
   numeric ID) and generate an **SMTP key**. The key is shown once.
4. Set these five variables on the Render service
   (Dashboard → cattlecare-ai → Environment):

   ```
   EMAIL_HOST          smtp-relay.brevo.com
   EMAIL_PORT          2525
   EMAIL_HOST_USER     <your Brevo SMTP login>
   EMAIL_HOST_PASSWORD <your Brevo SMTP key>
   DEFAULT_FROM_EMAIL  CattleCare AI <your-verified-sender@example.com>
   ```

   `DEFAULT_FROM_EMAIL` matters here. Left unset it defaults to
   `EMAIL_HOST_USER`, and a Brevo login is often not a real mailbox — the
   message would then be sent from an address that cannot receive a reply, or
   rejected outright as an unverified sender.

5. Saving the variables redeploys the service. Then confirm it works:

   ```bash
   # From the deployed site: request a reset for a real user, then read the log.
   # A success looks like:
   #   INFO core.mailer Email sent: 'CattleCare AI - Password Reset' -> someone@example.com
   ```

   The Render log is the only evidence either way, because the send happens on
   a background thread after the response has already gone out.

---

## Local development

Locally there is no port blocking, so Gmail works fine. Put this in `.env` in
the project root (same folder as `manage.py`):

```
EMAIL_HOST_USER=your_gmail@gmail.com
EMAIL_HOST_PASSWORD=your_16_character_app_password
```

`EMAIL_HOST_PASSWORD` must be a Gmail **App Password**, not the account
password — Google Account → Security → 2-Step Verification → App passwords.

Then check it:

```bash
python manage.py send_test_email you@example.com
```

**If you leave `.env` unset**, Django falls back to the console backend: the
message is printed to the terminal instead of being sent. Nothing is
delivered, and nothing is broken — this is what lets a fresh clone run with no
configuration. `core.mailer.is_smtp_configured()` is how the views know not to
promise an inbox that nothing was sent to.

---

## Recovering an account without email

If someone is locked out and email is not working yet:

```bash
python manage.py set_user_password someone@example.com NewSecurePassword123
```

They can then log in with their **username** and that password.

---

## Troubleshooting

Read the Render logs first — `core.mailer` logs every send and every failure.

| Log line | Meaning | Fix |
| --- | --- | --- |
| `OSError: [Errno 101] Network is unreachable` | Render is blocking the port | Use port 2525, or upgrade to a paid instance |
| `SMTPAuthenticationError: (535, ...)` | Port is fine, credentials are wrong | Re-check `EMAIL_HOST_USER` / `EMAIL_HOST_PASSWORD` |
| `SMTPSenderRefused` | Sender not verified with the provider | Verify the `DEFAULT_FROM_EMAIL` address |
| Nothing at all, and mail arrives nowhere | Console backend is in use | `EMAIL_HOST_USER` or `EMAIL_HOST_PASSWORD` is unset |
| `Email ... not sent: no valid recipient address` | The vet or user row has a blank email | Fill in the address on their profile |

A password reset says "if an account exists with that email…" whether or not
one does. That is deliberate — it keeps the form from confirming which
addresses are registered — so it is never evidence that mail was sent. Use the
log.
