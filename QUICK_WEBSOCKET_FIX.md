# Quick WebSocket Fix - Error 1006

## The Problem

Error 1006 = Connection failed during handshake (never established)

## Most Likely Cause

**Server not running with Daphne** or connection being rejected

## Quick Fix Steps

### Step 1: Check Server Logs

When you try to connect, do you see ANY of these logs?

```
🔍 WebSocket connection attempt - Path: /ws/notifications/, Query: token=...
```

**If NO logs appear:**

- Server is NOT running with Daphne
- Use: `daphne -b 0.0.0.0 -p 8000 enhancefund.asgi:application`

**If logs appear but connection fails:**

- Check what error message appears
- Share the server logs

### Step 2: Verify Server Command

```bash
# ❌ WRONG - This won't work for WebSockets
python manage.py runserver

# ✅ CORRECT - Use Daphne
daphne -b 0.0.0.0 -p 8000 enhancefund.asgi:application
```

### Step 3: Test Connection

In browser console:

```javascript
const token = "aec8e0e9a0b3d8637b8926a5adffb44e487330ec";
const ws = new WebSocket(
  `ws://127.0.0.1:8000/ws/notifications/?token=${token}`
);

ws.onopen = () => console.log("✅ Connected!");
ws.onerror = (e) => console.error("❌ Error:", e);
ws.onclose = (e) => console.log("🔌 Closed:", e.code, e.reason);
```

### Step 4: Check Server Logs Output

Share what you see in server logs when connecting.

## What to Share

1. **Server logs** - What appears when you try to connect?
2. **Server command** - How are you starting the server?
3. **Any error messages** - From server or browser console

## Expected Server Logs (When Working)

```
🔍 WebSocket connection attempt - Path: /ws/notifications/, Query: token=aec8e0e9a0b3d8637b8926a5adffb44e487330ec
🔑 Token extracted: aec8e0e9a0...
✅ Token authenticated for user: sandra.investor@gmail.com (ID: 56)
🔍 Consumer connect called - Path: /ws/notifications/, User: <User: sandra.investor@gmail.com>
✅ WebSocket connected for user: sandra.investor@gmail.com (ID: 56)
```

If you're NOT seeing these, the connection isn't reaching the server properly.
