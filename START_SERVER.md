# How to Start the Server with WebSocket Support

## Important: WebSocket Support Required

For real-time notifications to work, you **MUST** use **Daphne** instead of the regular `python manage.py runserver` command.

## Option 1: Run Daphne Directly (Recommended for Development)

```bash
daphne -b 0.0.0.0 -p 8000 enhancefund.asgi:application
```

**Yes, you need to run this command every time you start the server.**

### Make it Easier - Create a Script

**Windows (create `start_server.bat`):**

```batch
@echo off
echo Starting EnhanceFund server with WebSocket support...
daphne -b 0.0.0.0 -p 8000 enhancefund.asgi:application
```

**Linux/Mac (create `start_server.sh`):**

```bash
#!/bin/bash
echo "Starting EnhanceFund server with WebSocket support..."
daphne -b 0.0.0.0 -p 8000 enhancefund.asgi:application
```

Then make it executable:

```bash
chmod +x start_server.sh
```

Run it:

```bash
./start_server.sh
```

## Option 2: Update manage.py (Alternative)

You can modify `manage.py` to use Daphne by default, but this is not recommended as it changes Django's default behavior.

## Option 3: Use Both (HTTP + WebSocket)

Daphne handles both HTTP and WebSocket, so you don't need to run `runserver` separately. Daphne replaces it completely.

## Quick Start Commands

### First Time Setup

```bash
# 1. Install dependencies
pip install channels==4.0.0 daphne==4.1.0

# 2. Run migrations
python manage.py makemigrations users
python manage.py migrate

# 3. Start server with Daphne
daphne -b 0.0.0.0 -p 8000 enhancefund.asgi:application
```

### Every Time You Start the Server

```bash
daphne -b 0.0.0.0 -p 8000 enhancefund.asgi:application
```

## What Daphne Does

- ✅ Handles HTTP requests (like `runserver`)
- ✅ Handles WebSocket connections (for real-time notifications)
- ✅ Single server for everything

## Port Configuration

- Default: `-p 8000` (port 8000)
- Change port: `-p 8080` (for port 8080)
- Bind to all interfaces: `-b 0.0.0.0` (allows external connections)
- Local only: `-b 127.0.0.1` (localhost only)

## Troubleshooting

### Error: "daphne: command not found"

```bash
pip install daphne==4.1.0
```

### Error: "channels not installed"

```bash
pip install channels==4.0.0
```

### WebSocket not connecting?

1. Make sure you're using Daphne (not `runserver`)
2. Check that `ASGI_APPLICATION` is set in `settings.py`
3. Verify WebSocket URL: `ws://localhost:8000/ws/notifications/?token=YOUR_TOKEN`

## Production Deployment

For production, use a process manager like:

- **Supervisor** (Linux)
- **systemd** (Linux)
- **PM2** (Node.js process manager, works with Python too)

Example with PM2:

```bash
pm2 start "daphne -b 0.0.0.0 -p 8000 enhancefund.asgi:application" --name enhancefund
```

## Summary

**Yes, you need to run the daphne command every time you start the server.**

The command is:

```bash
daphne -b 0.0.0.0 -p 8000 enhancefund.asgi:application
```

Create a script file to make it easier to run!
