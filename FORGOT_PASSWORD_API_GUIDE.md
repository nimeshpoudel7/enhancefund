# Forgot Password API Documentation

This document provides comprehensive information about the Forgot Password and Reset Password APIs implemented in the EnhanceFund application.

## Overview

The password recovery system consists of two main API endpoints:

1. **Forgot Password API** - Initiates the password reset process
2. **Reset Password API** - Completes the password reset with a valid token

## Features

✅ Secure token-based password reset  
✅ Email notification with reset link  
✅ Token expiration (24 hours)  
✅ One-time use tokens  
✅ Password strength validation  
✅ Automatic invalidation of old tokens  
✅ Email confirmation after password change

---

## API Endpoints

### 1. Forgot Password API

**Endpoint:** `POST /api/v1/users/auth/forgot-password/`

**Description:** Request a password reset link. The system will send an email with a reset token to the user's registered email address.

**Authentication:** Not required (public endpoint)

#### Request Body

```json
{
  "email": "user@example.com"
}
```

#### Success Response

**Status Code:** `200 OK`

```json
{
  "status": 200,
  "message": "Password reset link has been sent to your email",
  "data": {
    "email": "user@example.com"
  }
}
```

#### Error Response

**Status Code:** `400 BAD REQUEST`

```json
{
  "status": 400,
  "message": "Invalid email address",
  "data": {
    "email": ["Enter a valid email address."]
  }
}
```

#### Security Notes

- For security reasons, the API returns a success message even if the email doesn't exist in the system
- This prevents attackers from discovering valid email addresses
- Only registered users will actually receive the reset email

---

### 2. Reset Password API

**Endpoint:** `POST /api/v1/users/auth/reset-password/`

**Description:** Reset the password using the token received via email.

**Authentication:** Not required (uses token from email)

#### Request Body

```json
{
  "token": "Xy9Z1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p7q8r9s0t1u2v3w4x5y6z",
  "new_password": "NewSecurePassword123!",
  "confirm_password": "NewSecurePassword123!"
}
```

#### Success Response

**Status Code:** `200 OK`

```json
{
  "status": 200,
  "message": "Password has been reset successfully. You can now login with your new password."
}
```

#### Error Responses

**Invalid or Expired Token**

**Status Code:** `400 BAD REQUEST`

```json
{
  "status": 400,
  "message": "Invalid request",
  "data": {
    "token": ["Token is invalid or has expired."]
  }
}
```

**Password Mismatch**

**Status Code:** `400 BAD REQUEST`

```json
{
  "status": 400,
  "message": "Invalid request",
  "data": {
    "password": ["Password fields didn't match."]
  }
}
```

**Weak Password**

**Status Code:** `400 BAD REQUEST`

```json
{
  "status": 400,
  "message": "Invalid request",
  "data": {
    "new_password": [
      "This password is too common.",
      "This password is too short. It must contain at least 8 characters."
    ]
  }
}
```

---

## Complete Usage Flow

### Step 1: User Requests Password Reset

```bash
curl -X POST http://localhost:8000/api/v1/users/auth/forgot-password/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john.doe@example.com"
  }'
```

### Step 2: User Receives Email

The user will receive an email with a reset link that looks like:

```
Subject: Password Reset Request

Dear John,

We received a request to reset your password. Click the link below to reset your password:

https://yourdomain.com/reset-password/Xy9Z1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p7q8r9s0t1u2v3w4x5y6z

This link will expire in 24 hours.

If you didn't request this, please ignore this email.
```

### Step 3: User Resets Password

```bash
curl -X POST http://localhost:8000/api/v1/users/auth/reset-password/ \
  -H "Content-Type: application/json" \
  -d '{
    "token": "Xy9Z1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p7q8r9s0t1u2v3w4x5y6z",
    "new_password": "MyNewSecurePassword123!",
    "confirm_password": "MyNewSecurePassword123!"
  }'
```

### Step 4: User Receives Confirmation Email

After successful password reset, the user receives a confirmation email:

```
Subject: Your Password Has Been Changed

Dear John,

Your password was successfully changed on 2025-10-10 14:30:00.

If you didn't make this change, please contact support immediately.
```

### Step 5: User Logs In

```bash
curl -X POST http://localhost:8000/api/v1/users/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john.doe@example.com",
    "password": "MyNewSecurePassword123!"
  }'
```

---

## Frontend Integration Example

### React/JavaScript Example

```javascript
// Forgot Password Component
const ForgotPassword = () => {
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  const handleForgotPassword = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await fetch(
        "http://localhost:8000/api/v1/users/auth/forgot-password/",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ email }),
        }
      );

      const data = await response.json();

      if (response.ok) {
        setMessage("Password reset link sent! Check your email.");
      } else {
        setMessage("Error: " + data.message);
      }
    } catch (error) {
      setMessage("An error occurred. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleForgotPassword}>
      <input
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        placeholder="Enter your email"
        required
      />
      <button type="submit" disabled={loading}>
        {loading ? "Sending..." : "Send Reset Link"}
      </button>
      {message && <p>{message}</p>}
    </form>
  );
};

// Reset Password Component
const ResetPassword = () => {
  const [token, setToken] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // Extract token from URL parameter
    const params = new URLSearchParams(window.location.search);
    const tokenFromUrl = params.get("token");
    if (tokenFromUrl) {
      setToken(tokenFromUrl);
    }
  }, []);

  const handleResetPassword = async (e) => {
    e.preventDefault();

    if (newPassword !== confirmPassword) {
      setMessage("Passwords do not match!");
      return;
    }

    setLoading(true);

    try {
      const response = await fetch(
        "http://localhost:8000/api/v1/users/auth/reset-password/",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            token,
            new_password: newPassword,
            confirm_password: confirmPassword,
          }),
        }
      );

      const data = await response.json();

      if (response.ok) {
        setMessage("Password reset successful! You can now login.");
        // Redirect to login page after 2 seconds
        setTimeout(() => {
          window.location.href = "/login";
        }, 2000);
      } else {
        setMessage("Error: " + (data.message || "Failed to reset password"));
      }
    } catch (error) {
      setMessage("An error occurred. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleResetPassword}>
      <input
        type="password"
        value={newPassword}
        onChange={(e) => setNewPassword(e.target.value)}
        placeholder="New Password"
        required
      />
      <input
        type="password"
        value={confirmPassword}
        onChange={(e) => setConfirmPassword(e.target.value)}
        placeholder="Confirm Password"
        required
      />
      <button type="submit" disabled={loading}>
        {loading ? "Resetting..." : "Reset Password"}
      </button>
      {message && <p>{message}</p>}
    </form>
  );
};
```

---

## Database Schema

### PasswordResetToken Model

```python
class PasswordResetToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
```

**Fields:**

- `user`: Foreign key to the User model
- `token`: Unique, secure URL-safe token (32 bytes)
- `created_at`: Timestamp when token was created
- `expires_at`: Expiration time (24 hours from creation)
- `is_used`: Flag to prevent token reuse

---

## Security Features

### 1. Token Generation

- Uses `secrets.token_urlsafe(32)` for cryptographically secure random tokens
- Tokens are 43 characters long (URL-safe base64 encoding)

### 2. Token Expiration

- Tokens automatically expire after 24 hours
- Expired tokens cannot be used to reset password

### 3. One-Time Use

- Tokens are marked as used after successful password reset
- Used tokens cannot be reused

### 4. Old Token Invalidation

- When a new reset request is made, all previous unused tokens for that user are invalidated
- Prevents accumulation of valid tokens

### 5. Password Validation

- Django's built-in password validators ensure strong passwords:
  - Minimum 8 characters
  - Not too similar to user information
  - Not a common password
  - Not entirely numeric

### 6. Email Privacy

- System doesn't reveal if an email exists or not
- Prevents email enumeration attacks

---

## Email Configuration

Make sure your Django settings have email configured:

```python
# settings.py

# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'  # or your SMTP server
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
DEFAULT_FROM_EMAIL = 'noreply@enhancefund.com'

# Site Configuration
SITE_URL = 'https://yourdomain.com'
SITE_NAME = 'EnhanceFund'
SUPPORT_EMAIL = 'support@enhancefund.com'
```

---

## Testing

### Manual Testing with curl

**1. Test Forgot Password:**

```bash
curl -X POST http://localhost:8000/api/v1/users/auth/forgot-password/ \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com"}'
```

**2. Check your email for the token**

**3. Test Reset Password:**

```bash
curl -X POST http://localhost:8000/api/v1/users/auth/reset-password/ \
  -H "Content-Type: application/json" \
  -d '{
    "token": "YOUR_TOKEN_FROM_EMAIL",
    "new_password": "NewPassword123!",
    "confirm_password": "NewPassword123!"
  }'
```

### Test Cases

1. ✅ Valid email receives reset link
2. ✅ Invalid email returns generic success message
3. ✅ Valid token successfully resets password
4. ✅ Expired token is rejected
5. ✅ Used token is rejected
6. ✅ Password mismatch is caught
7. ✅ Weak passwords are rejected
8. ✅ User receives confirmation email after reset

---

## Troubleshooting

### Issue: Email not being sent

**Solution:**

1. Check email configuration in `settings.py`
2. Verify SMTP credentials
3. Check if email service allows less secure apps
4. Look at Django logs for email errors

### Issue: Token expired error

**Solution:**

- Tokens expire after 24 hours
- Request a new password reset link

### Issue: Token invalid error

**Solution:**

- Ensure you're using the complete token from the email
- Token might have been used already
- Request a new password reset link

---

## Migration Commands

After implementing the forgot password feature, run these commands:

```bash
# Create migration
python manage.py makemigrations users

# Apply migration
python manage.py migrate users
```

This will create the `password_reset_tokens` table in your database.

---

## Additional Notes

- Password reset tokens are stored in the database and should be cleaned up periodically
- Consider adding a cron job to delete expired tokens older than 7 days
- All password reset activities should be logged for security auditing
- Consider adding rate limiting to prevent abuse

---

## Support

For issues or questions, contact the development team or refer to the main project documentation.

**Last Updated:** October 10, 2025


