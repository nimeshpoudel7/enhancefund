# WebSocket Connection Debugging Guide

## Current Issue
WebSocket connection fails or disconnects immediately.

## Debugging Steps

### 1. Check Server is Running with Daphne

**IMPORTANT:** You MUST use Daphne, not `runserver`:

```bash
# ❌ WRONG - This won't work for WebSockets
python manage.py runserver

# ✅ CORRECT - Use Daphne
daphne -b 0.0.0.0 -p 8000 enhancefund.asgi:application
```

### 2. Check Server Logs

When you try to connect, you should see these logs in order:

1. **Middleware logs:**
   ```
   🔍 WebSocket connection attempt - Path: /ws/notifications/, Query: token=...
   🔑 Token extracted: aec8e0e9a0...
   ✅ Token authenticated for user: sandra.investor@gmail.com (ID: 56)
   ```

2. **Consumer logs:**
   ```
   🔍 Consumer connect called - Path: /ws/notifications/, User: <User: sandra.investor@gmail.com>
   ✅ WebSocket connected for user: sandra.investor@gmail.com (ID: 56)
   ```

### 3. Test Connection URL

**Correct format:**
```
ws://127.0.0.1:8000/ws/notifications/?token=YOUR_TOKEN
```

**Common mistakes:**
- ❌ `http://` instead of `ws://`
- ❌ Missing `/ws/` prefix
- ❌ Wrong token format
- ❌ Missing `?token=` query parameter

### 4. Test in Browser Console

Open browser console and run:

```javascript
const token = "YOUR_TOKEN_HERE";
const ws = new WebSocket(`ws://127.0.0.1:8000/ws/notifications/?token=${token}`);

ws.onopen = () => {
  console.log("✅ Connected!");
};

ws.onmessage = (e) => {
  console.log("📨 Message:", JSON.parse(e.data));
};

ws.onerror = (e) => {
  console.error("❌ Error:", e);
};

ws.onclose = (e) => {
  console.log("🔌 Closed:", e.code, e.reason, "Clean:", e.wasClean);
};
```

### 5. Check What Logs You're Seeing

**If you see NO logs:**
- Server might not be running with Daphne
- URL pattern might not be matching
- Check if server is actually receiving the connection

**If you see middleware logs but NO consumer logs:**
- Routing pattern might not match
- Check the path in middleware logs

**If you see "User not authenticated":**
- Token is invalid or expired
- User account is inactive
- Token not being parsed correctly

**If connection closes immediately:**
- Check close code in logs
- Check if frontend is closing it
- Check for errors in consumer

### 6. Verify Token is Valid

Test token with REST API first:

```bash
curl http://127.0.0.1:8000/api/notifications/ \
  -H "Authorization: Token YOUR_TOKEN"
```

If this works, the token is valid. If not, get a new token.

### 7. Check Channel Layers

Make sure `CHANNEL_LAYERS` is configured in `settings.py`:

```python
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    },
}
```

### 8. Verify ASGI Application

Check `enhancefund/asgi.py`:

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

### 9. Common Issues and Fixes

#### Issue: "Connection refused"
- **Fix:** Make sure Daphne is running, not `runserver`

#### Issue: "404 Not Found"
- **Fix:** Check URL pattern matches `/ws/notifications/`
- **Fix:** Verify routing is registered in `asgi.py`

#### Issue: "401 Unauthorized"
- **Fix:** Check token is valid
- **Fix:** Verify token is in query string: `?token=...`

#### Issue: Connects then immediately disconnects
- **Fix:** Check frontend isn't closing connection
- **Fix:** Add ping/pong keep-alive
- **Fix:** Check for errors in server logs

### 10. Full Test Sequence

1. **Start server:**
   ```bash
   daphne -b 0.0.0.0 -p 8000 enhancefund.asgi:application
   ```

2. **Test in browser console:**
   ```javascript
   const ws = new WebSocket('ws://127.0.0.1:8000/ws/notifications/?token=YOUR_TOKEN');
   ws.onopen = () => console.log('Connected!');
   ws.onmessage = (e) => console.log('Message:', JSON.parse(e.data));
   ws.onerror = (e) => console.error('Error:', e);
   ws.onclose = (e) => console.log('Closed:', e.code);
   ```

3. **Check server logs** - Should see:
   - Middleware authentication logs
   - Consumer connection logs
   - Connection confirmation message

4. **Send ping:**
   ```javascript
   ws.send(JSON.stringify({type: 'ping'}));
   ```

5. **Should receive pong:**
   ```json
   {"type": "pong", "message": "pong"}
   ```

## What to Report

If still having issues, provide:

1. **Server logs** - Full output when trying to connect
2. **Connection URL** - Exact URL you're using
3. **Error message** - From browser console or Postman
4. **Close code** - If connection closes, what code?
5. **Server command** - How you're starting the server

## Quick Checklist

- [ ] Server running with `daphne` (not `runserver`)
- [ ] URL starts with `ws://` (not `http://`)
- [ ] URL includes `/ws/notifications/`
- [ ] Token is in query string: `?token=...`
- [ ] Token is valid (test with REST API)
- [ ] `CHANNEL_LAYERS` configured in settings
- [ ] `ASGI_APPLICATION` set in settings
- [ ] Routing registered in `asgi.py`
- [ ] No errors in server logs

