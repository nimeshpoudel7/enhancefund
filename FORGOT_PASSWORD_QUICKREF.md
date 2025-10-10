# Forgot Password API - Quick Reference

## 🔑 Endpoints

### 1. Request Password Reset

```
POST /api/v1/users/auth/forgot-password/
```

**Body:**

```json
{
  "email": "user@example.com"
}
```

**Response:**

```json
{
  "status": 200,
  "message": "Password reset link has been sent to your email",
  "data": {
    "email": "user@example.com"
  }
}
```

---

### 2. Reset Password

```
POST /api/v1/users/auth/reset-password/
```

**Body:**

```json
{
  "token": "abc123...xyz",
  "new_password": "NewPassword123!",
  "confirm_password": "NewPassword123!"
}
```

**Response:**

```json
{
  "status": 200,
  "message": "Password has been reset successfully. You can now login with your new password."
}
```

---

## 🔧 Setup Checklist

- [x] PasswordResetToken model created
- [x] Forgot password serializers added
- [x] API views implemented
- [x] URL routes configured
- [ ] Run migrations: `python manage.py migrate users`
- [ ] Configure email settings in `settings.py`
- [ ] Test the endpoints

---

## ⚙️ Email Configuration

Add to `settings.py`:

```python
# Email Settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_PASSWORD')
DEFAULT_FROM_EMAIL = 'noreply@enhancefund.com'

# Site Settings
SITE_URL = 'https://yourdomain.com'
SITE_NAME = 'EnhanceFund'
SUPPORT_EMAIL = 'support@enhancefund.com'
```

Add to `.env`:

```
EMAIL_USER=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
```

---

## 🧪 Quick Test

```bash
# 1. Request password reset
curl -X POST http://localhost:8000/api/v1/users/auth/forgot-password/ \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com"}'

# 2. Check email, copy token

# 3. Reset password
curl -X POST http://localhost:8000/api/v1/users/auth/reset-password/ \
  -H "Content-Type: application/json" \
  -d '{
    "token": "YOUR_TOKEN",
    "new_password": "NewPass123!",
    "confirm_password": "NewPass123!"
  }'
```

---

## 📋 Password Requirements

- Minimum 8 characters
- Not too similar to email/username
- Not a common password
- Not entirely numeric

---

## ⏱️ Token Lifetime

- **Valid for:** 24 hours
- **One-time use:** Yes
- **Auto-invalidated:** When new reset requested
