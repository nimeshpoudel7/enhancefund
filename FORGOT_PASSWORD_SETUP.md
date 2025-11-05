# Forgot Password Feature - Setup Guide

## ✅ What Has Been Implemented

The forgot password feature has been fully implemented with the following components:

### 1. Database Model

- **PasswordResetToken** model in `users/models.py`
  - Secure token generation
  - 24-hour expiration
  - One-time use tokens
  - Auto-invalidation of old tokens

### 2. API Endpoints

- **POST** `/api/v1/users/auth/forgot-password/` - Request password reset
- **POST** `/api/v1/users/auth/reset-password/` - Reset password with token

### 3. Serializers

- **ForgotPasswordSerializer** - Validates email input
- **ResetPasswordSerializer** - Validates token and new password

### 4. Views

- **ForgotPasswordAPI** - Handles password reset requests
- **ResetPasswordAPI** - Handles password updates

### 5. Email Integration

- Uses existing EmailService from `enhancefund/email_utils.py`
- Sends password reset link to user
- Sends confirmation email after password change

---

## 🚀 Setup Instructions

### Step 1: Run Database Migration

```bash
python manage.py migrate users
```

This creates the `password_reset_tokens` table in your database.

### Step 2: Configure Email Settings

Add these environment variables to your `.env` file:

```env
# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-specific-password
DEFAULT_FROM_EMAIL=noreply@enhancefund.com

# Site Configuration
SITE_URL=http://localhost:3000
SITE_NAME=EnhanceFund
SUPPORT_EMAIL=support@enhancefund.com
```

#### For Gmail Users:

1. Enable 2-Factor Authentication on your Google account
2. Go to: https://myaccount.google.com/apppasswords
3. Generate an App Password for "Mail"
4. Use the 16-character password as `EMAIL_HOST_PASSWORD`

#### For Other Email Providers:

Update `EMAIL_HOST`, `EMAIL_PORT`, and credentials accordingly.

### Step 3: Create Email Templates

Create the following email template files (referenced in `email_utils.py`):

**File:** `templates/emails/password_reset.html`

```html
<!DOCTYPE html>
<html>
  <head>
    <style>
      body {
        font-family: Arial, sans-serif;
        line-height: 1.6;
        color: #333;
      }
      .container {
        max-width: 600px;
        margin: 0 auto;
        padding: 20px;
      }
      .button {
        background-color: #007bff;
        color: white;
        padding: 12px 24px;
        text-decoration: none;
        border-radius: 4px;
        display: inline-block;
        margin: 20px 0;
      }
      .footer {
        margin-top: 30px;
        padding-top: 20px;
        border-top: 1px solid #ddd;
        font-size: 12px;
        color: #666;
      }
    </style>
  </head>
  <body>
    <div class="container">
      <h2>Password Reset Request</h2>
      <p>Hi {{ first_name }},</p>
      <p>
        We received a request to reset your password for your {{ site_name }}
        account.
      </p>
      <p>Click the button below to reset your password:</p>
      <a href="{{ reset_link }}" class="button">Reset Password</a>
      <p>Or copy and paste this link into your browser:</p>
      <p style="word-break: break-all;">{{ reset_link }}</p>
      <p>This link will expire in {{ valid_hours }} hours.</p>
      <p>
        If you didn't request this, please ignore this email. Your password will
        remain unchanged.
      </p>
      <div class="footer">
        <p>Need help? Contact us at {{ support_email }}</p>
        <p>&copy; 2025 {{ site_name }}. All rights reserved.</p>
      </div>
    </div>
  </body>
</html>
```

**File:** `templates/emails/password_reset.txt`

```text
Password Reset Request

Hi {{ first_name }},

We received a request to reset your password for your {{ site_name }} account.

Click the link below to reset your password:
{{ reset_link }}

This link will expire in {{ valid_hours }} hours.

If you didn't request this, please ignore this email. Your password will remain unchanged.

Need help? Contact us at {{ support_email }}

© 2025 {{ site_name }}. All rights reserved.
```

**File:** `templates/emails/password_changed.html`

```html
<!DOCTYPE html>
<html>
  <head>
    <style>
      body {
        font-family: Arial, sans-serif;
        line-height: 1.6;
        color: #333;
      }
      .container {
        max-width: 600px;
        margin: 0 auto;
        padding: 20px;
      }
      .alert {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 12px;
        border-radius: 4px;
        margin: 20px 0;
      }
      .footer {
        margin-top: 30px;
        padding-top: 20px;
        border-top: 1px solid #ddd;
        font-size: 12px;
        color: #666;
      }
    </style>
  </head>
  <body>
    <div class="container">
      <h2>Password Changed Successfully</h2>
      <p>Hi {{ first_name }},</p>
      <div class="alert">
        <strong
          >Your password was successfully changed on {{ timestamp }}.</strong
        >
      </div>
      <p>If you made this change, you can safely ignore this email.</p>
      <p>
        If you didn't make this change, please contact our support team
        immediately at {{ support_email }}.
      </p>
      <div class="footer">
        <p>Need help? Contact us at {{ support_email }}</p>
        <p>&copy; 2025 {{ site_name }}. All rights reserved.</p>
      </div>
    </div>
  </body>
</html>
```

**File:** `templates/emails/password_changed.txt`

```text
Password Changed Successfully

Hi {{ first_name }},

Your password was successfully changed on {{ timestamp }}.

If you made this change, you can safely ignore this email.

If you didn't make this change, please contact our support team immediately at {{ support_email }}.

Need help? Contact us at {{ support_email }}

© 2025 {{ site_name }}. All rights reserved.
```

### Step 4: Test the Feature

#### Test 1: Request Password Reset

```bash
curl -X POST http://localhost:8000/api/v1/users/auth/forgot-password/ \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com"}'
```

#### Test 2: Check Email

- Check the inbox for `test@example.com`
- Copy the reset token from the email

#### Test 3: Reset Password

```bash
curl -X POST http://localhost:8000/api/v1/users/auth/reset-password/ \
  -H "Content-Type: application/json" \
  -d '{
    "token": "YOUR_TOKEN_HERE",
    "new_password": "NewPassword123!",
    "confirm_password": "NewPassword123!"
  }'
```

#### Test 4: Login with New Password

```bash
curl -X POST http://localhost:8000/api/v1/users/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "NewPassword123!"
  }'
```

---

## 📁 Files Modified

1. ✅ `users/models.py` - Added PasswordResetToken model
2. ✅ `users/serializers.py` - Added ForgotPasswordSerializer and ResetPasswordSerializer
3. ✅ `users/auth/view.py` - Added ForgotPasswordAPI and ResetPasswordAPI views
4. ✅ `users/urls.py` - Added URL routes for forgot/reset password
5. ✅ `enhancefund/settings.py` - Added email configuration
6. ✅ `users/migrations/0012_passwordresettoken.py` - Database migration (created)

---

## 🔐 Security Features

- ✅ Cryptographically secure token generation
- ✅ Token expiration (24 hours)
- ✅ One-time use tokens
- ✅ Automatic invalidation of old tokens
- ✅ Password strength validation
- ✅ Email enumeration protection
- ✅ Confirmation email after password change

---

## 🧪 For Development: Console Email Backend

If you don't want to configure SMTP during development, you can use the console backend:

In `settings.py` or `.env`:

```python
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

This will print emails to the console instead of sending them.

---

## 📝 Additional Recommendations

### 1. Add Rate Limiting

Consider adding rate limiting to prevent abuse:

```python
from django.core.cache import cache

# In ForgotPasswordAPI
def post(self, request, *args, **kwargs):
    email = request.data.get('email')
    cache_key = f"password_reset_{email}"

    if cache.get(cache_key):
        return enhance_response(
            status=status.HTTP_429_TOO_MANY_REQUESTS,
            message="Please wait before requesting another reset"
        )

    # Set cache for 5 minutes
    cache.set(cache_key, True, 300)
    # ... rest of the code
```

### 2. Clean Up Old Tokens

Add a management command to delete expired tokens:

**File:** `users/management/commands/cleanup_reset_tokens.py`

```python
from django.core.management.base import BaseCommand
from django.utils import timezone
from users.models import PasswordResetToken

class Command(BaseCommand):
    help = 'Delete expired password reset tokens'

    def handle(self, *args, **options):
        deleted = PasswordResetToken.objects.filter(
            expires_at__lt=timezone.now()
        ).delete()
        self.stdout.write(
            self.style.SUCCESS(f'Deleted {deleted[0]} expired tokens')
        )
```

Run with: `python manage.py cleanup_reset_tokens`

### 3. Add to Cron Job

Schedule the cleanup command to run daily:

```bash
0 2 * * * cd /path/to/project && python manage.py cleanup_reset_tokens
```

---

## 🆘 Troubleshooting

### Issue: "SMTPAuthenticationError"

**Solution:**

- Verify email credentials
- For Gmail, ensure you're using an App Password, not your regular password
- Check if "Less secure app access" is enabled (if not using 2FA)

### Issue: Emails not being received

**Solution:**

- Check spam/junk folder
- Verify EMAIL_HOST_USER is correct
- Check Django logs for error messages
- Try using console backend for testing

### Issue: "Token is invalid or has expired"

**Solution:**

- Tokens expire after 24 hours
- Tokens can only be used once
- Request a new password reset

---

## 📚 Additional Documentation

- Full API Documentation: `FORGOT_PASSWORD_API_GUIDE.md`
- Quick Reference: `FORGOT_PASSWORD_QUICKREF.md`

---

## ✨ Summary

The forgot password feature is now fully implemented and ready to use! Just complete the setup steps above, and your users will be able to reset their passwords securely.

**Last Updated:** October 10, 2025


