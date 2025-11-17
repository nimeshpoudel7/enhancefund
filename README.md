## Install and Run
1. Clone the repository
2. Create virtual environment
# EnhanceFund

## Install and Run

1. Clone the repository
2. Create virtual environment

```bash
python3 -m venv .venv
```

3. Activate the virtual environment

```bash
.venv\Scripts\activate
```

4. Install the dependencies

```bash
pip install -r requirements.txt
```

5. Make migrations and migrate

```bash
python manage.py makemigrations
python manage.py migrate
```

6. Run the server

**For WebSocket support (Real-time Notifications):**
```bash
# Windows
start_server.bat

# Linux/Mac
chmod +x start_server.sh
./start_server.sh

# Or manually:
daphne -b 0.0.0.0 -p 8000 enhancefund.asgi:application
```

**Note:** For real-time notifications to work, you MUST use Daphne instead of `runserver`.

**Without WebSocket (Regular HTTP only):**
```bash
python manage.py runserver
```

## Email (SMTP) setup & test

This project supports sending real emails via SMTP. For local development the default is to print emails to the console (so you can test password reset flows without real SMTP credentials). To send real email you must add SMTP-related environment variables to your `.env` file.

Recommended environment variables (add to your `.env`):

- For SendGrid (SMTP):

```env
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=YOUR_SENDGRID_API_KEY
DEFAULT_FROM_EMAIL=yourapp@yourdomain.com
EMAIL_USE_CONSOLE=False
```

- For Gmail (less recommended for production):

```env
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your@gmail.com
EMAIL_HOST_PASSWORD=your-app-password-or-oauth-token
DEFAULT_FROM_EMAIL=your@gmail.com
EMAIL_USE_CONSOLE=False
```

How to test after adding env vars:

1. Restart your Django server (or re-export env vars).
2. Run the management command to send a test email:

```bash
python manage.py send_test_email --to you@example.com --subject "Test" --body "Test body"
```

The command prints which backend and SMTP host/port are being used, and either confirms success or prints the error returned by the SMTP library.

If you prefer to keep console output even with SMTP configured, set `EMAIL_USE_CONSOLE=True` in the `.env` while keeping `DEBUG=True`.
