# Sending real password reset emails to users

When a user (e.g. Ree with rifilwe.mbengo@students.uz.ac.zw) forgets their password and requests a reset, the system sends the **reset link and OTP to the email they used when they registered**. Right now **no real email is sent** — the message only appears in the server terminal. To fix this, configure a `.env` file as below.

---

## Why Ree (and others) don't get the reset email

The app is using the **console** email backend: the reset email is **printed in the terminal** where you run `runserver`, and **nothing is sent to rifilwe.mbengo@students.uz.ac.zw**. The database and the “Forgot password” flow are correct; only the email delivery is not configured.

---

## Quick setup (Gmail) – do this once

1. **Create a file named `.env`** in the project root (same folder as `manage.py`). You can copy from `env_example.txt` and rename to `.env`, or create `.env` with exactly these two lines (use your own Gmail and App Password):

   ```
   EMAIL_HOST_USER=your_gmail@gmail.com
   EMAIL_HOST_PASSWORD=your_16_character_app_password
   ```

2. **Get a Gmail App Password** (do not use your normal Gmail password):
   - Open [Google Account → Security](https://myaccount.google.com/security)
   - Turn on **2-Step Verification** if it is off
   - Under “2-Step Verification”, click **App passwords**
   - Create a new app password for “Mail” and paste the 16-character password as `EMAIL_HOST_PASSWORD` in `.env`

3. **Restart the server** (stop and start again):
   ```bash
   python manage.py runserver
   ```

4. **Test that real email works:**
   ```bash
   python manage.py send_test_email rifilwe.mbengo@students.uz.ac.zw
   ```
   You should see “SMTP is configured” and “Test email sent to …”. Ree should receive the test email. After that, when he (or any user) uses “Forgot password”, the reset link will be sent to their registered email.

---

## What the system does

- User goes to **Forgot password** and enters their **email** (the one they registered with).
- The system finds their account and sends **one email** containing:
  - The password reset link
  - The one-time verification code (OTP)
- The email is sent to **that user’s registered email address** (e.g. riffymbengo@gmail.com). No one else receives it.

---

## If you don’t set `.env`

Without `EMAIL_HOST_USER` and `EMAIL_HOST_PASSWORD` in `.env` (or in the environment), Django uses the **console** backend: the reset email is only printed in the terminal where `runserver` is running, and **no real email** is sent. Users will not receive anything in their inbox until you complete the setup above.

---

## Recovering a single user without email (e.g. admin)

If you need to let one user log in before email is configured (e.g. admin locked out):

```bash
python manage.py set_user_password riffymbengo@gmail.com NewSecurePassword
```

They can then log in with their username and the new password.
