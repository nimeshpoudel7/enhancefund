# WebSocket Error 1006 - Abnormal Closure Fix

## What is Error 1006?

**Close Code 1006** = "Abnormal Closure"
- Connection closed without a proper close frame
- Usually means the connection **never established** (failed during handshake)
- `wasClean: false` confirms it wasn't a normal close

## Common Causes

### 1. Server Not Running with Daphne
❌ **Wrong:** `python manage.py runserver`  
✅ **Correct:** `daphne -b 0.0.0.0 -p 8000 enhancefund.asgi:application`

### 2. Authentication Failure
- Token invalid or expired
- User account inactive
- Token not being parsed correctly

### 3. Routing Issue
- URL pattern doesn't match
- WebSocket routing not registered

### 4. Server Rejecting Connection
- Server closes connection before accepting
- Error in `connect()` method

## Debugging Steps

### Step 1: Check Server Logs

When you try to connect, check your server logs. You should see:

**If connection reaches server:**
```
🔍 WebSocket connection attempt - Path: /ws/notifications/, Query: token=...
```

**If authentication works:**
```
🔑 Token extracted: aec8e0e9a0...
✅ Token authenticated for user: sandra.investor@gmail.com (ID: 56)
```

**If consumer is called:**
```
🔍 Consumer connect called - Path: /ws/notifications/, User: <User: ...>
```

**If connection succeeds:**
```
✅ WebSocket connected for user: sandra.investor@gmail.com (ID: 56)
```

### Step 2: Check What You're NOT Seeing

If you see **NO logs at all**, the connection isn't reaching the server:
- Server not running with Daphne
- Wrong URL
- Network/firewall blocking

If you see middleware logs but **NO consumer logs**, routing might be wrong.

If you see authentication logs but **connection rejected**, check the consumer error messages.

### Step 3: Test with Simple Client

Test in browser console:

```javascript
const token = "aec8e0e9a0b3d8637b8926a5adffb44e487330ec";
const ws = new WebSocket(`ws://127.0.0.1:8000/ws/notifications/?token=${token}`);

ws.onopen = () => {
  console.log("✅ Connected!");
};

ws.onerror = (error) => {
  console.error("❌ Error:", error);
  console.error("ReadyState:", ws.readyState); // 3 = CLOSED
};

ws.onclose = (event) => {
  console.log("🔌 Closed:", {
    code: event.code,
    reason: event.reason,
    wasClean: event.wasClean
  });
};
```

### Step 4: Verify Server is Running

```bash
# Check if Daphne is running
ps aux | grep daphne  # Linux/Mac
tasklist | findstr daphne  # Windows

# Or check if port 8000 is listening
netstat -an | grep 8000  # Linux/Mac
netstat -an | findstr 8000  # Windows
```

## Common Fixes

### Fix 1: Ensure Server is Running with Daphne

```bash
# Stop any existing server
# Then start with Daphne:
daphne -b 0.0.0.0 -p 8000 enhancefund.asgi:application
```

### Fix 2: Check Token is Valid

Test token with REST API:

```bash
curl http://127.0.0.1:8000/api/notifications/ \
  -H "Authorization: Token aec8e0e9a0b3d8637b8926a5adffb44e487330ec"
```

If this fails, get a new token.

### Fix 3: Check URL Format

**Correct:**
```
ws://127.0.0.1:8000/ws/notifications/?token=YOUR_TOKEN
```

**Common mistakes:**
- ❌ `http://` instead of `ws://`
- ❌ Missing `/ws/` prefix
- ❌ Wrong path
- ❌ Token not in query string

### Fix 4: Check Server Configuration

Verify in `enhancefund/settings.py`:

```python
ASGI_APPLICATION = 'enhancefund.asgi.application'

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    },
}
```

### Fix 5: Check ASGI Configuration

Verify `enhancefund/asgi.py`:

```python
application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": TokenAuthMiddleware(
        URLRouter(
            users_routing.websocket_urlpatterns
        )
    ),
})
```

## What to Check in Your Case

Based on your error (1006, wasClean: false), check:

1. **Server logs** - Are you seeing any connection attempts?
2. **Server command** - Are you using `daphne` not `runserver`?
3. **Token validity** - Test with REST API
4. **URL format** - Verify it's exactly: `ws://127.0.0.1:8000/ws/notifications/?token=...`

## Expected Server Logs

When connection works, you should see:

```
🔍 WebSocket connection attempt - Path: /ws/notifications/, Query: token=aec8e0e9a0b3d8637b8926a5adffb44e487330ec
🔑 Token extracted: aec8e0e9a0...
✅ Token authenticated for user: sandra.investor@gmail.com (ID: 56)
🔍 Consumer connect called - Path: /ws/notifications/, User: <User: sandra.investor@gmail.com>
✅ WebSocket connected for user: sandra.investor@gmail.com (ID: 56)
```

If you're **NOT seeing these logs**, the connection isn't reaching the server.

## Quick Test

Run this Python test script:

```bash
python test_websocket.py
```

This will show you exactly what's happening.

## Next Steps

1. **Check server logs** when you try to connect
2. **Verify server is running with Daphne**
3. **Test token with REST API**
4. **Share server logs** so we can see what's happening

The 1006 error means the connection is failing before it can establish. The server logs will tell us exactly why.

