# WebSocket Connection Troubleshooting Guide

## Common Issues and Solutions

### Issue 1: WebSocket Connection Failed

**Symptoms:**
- Browser console shows: `WebSocket connection to 'ws://127.0.0.1:8000/ws/notifications/?token=...' failed`
- No error message in server logs

**Solutions:**

1. **Check if server is running with Daphne:**
   ```bash
   # Must use Daphne, NOT runserver
   daphne -b 0.0.0.0 -p 8000 enhancefund.asgi:application
   ```

2. **Check server logs for errors:**
   - Look for authentication errors
   - Check if token is being parsed correctly
   - Verify user is being authenticated

3. **Verify token format:**
   - Token should be passed as: `?token=YOUR_TOKEN`
   - No spaces or special characters
   - Token must exist in database

4. **Test token manually:**
   ```python
   from rest_framework.authtoken.models import Token
   from users.models import User
   
   user = User.objects.get(email='your@email.com')
   token, created = Token.objects.get_or_create(user=user)
   print(f"Token: {token.key}")
   ```

### Issue 2: Authentication Failed

**Symptoms:**
- Connection closes immediately
- Server logs show: "WebSocket connection rejected: User not authenticated"

**Solutions:**

1. **Check token in database:**
   ```python
   from rest_framework.authtoken.models import Token
   token = Token.objects.get(key='your_token_here')
   print(f"User: {token.user.email}")
   ```

2. **Verify token is passed correctly:**
   - Frontend: `ws://localhost:8000/ws/notifications/?token=YOUR_TOKEN`
   - No `Bearer` prefix needed
   - Token should match exactly

3. **Check user is active:**
   ```python
   user = User.objects.get(email='your@email.com')
   print(f"Active: {user.is_active}")
   ```

### Issue 3: Connection Works But No Messages

**Symptoms:**
- WebSocket connects successfully
- No notifications received

**Solutions:**

1. **Check channel layer:**
   - Verify `CHANNEL_LAYERS` is configured in settings
   - For production, use Redis instead of InMemory

2. **Test notification creation:**
   - Add funds to wallet
   - Check if notification is created in database
   - Check server logs for WebSocket send errors

3. **Verify user ID matches:**
   - Room group name: `notifications_{user_id}`
   - Must match the user ID in the notification

### Issue 4: CORS/Origin Errors

**Symptoms:**
- Connection refused
- CORS errors in browser

**Solutions:**

1. **Check ALLOWED_HOSTS:**
   ```python
   ALLOWED_HOSTS = ['localhost', '127.0.0.1', ...]
   ```

2. **For WebSocket, CORS doesn't apply the same way**
   - Removed `AllowedHostsOriginValidator` from ASGI config
   - WebSocket uses origin validation differently

### Issue 5: Server Not Starting

**Symptoms:**
- Daphne command fails
- Import errors

**Solutions:**

1. **Install dependencies:**
   ```bash
   pip install channels==4.0.0 daphne==4.1.0
   ```

2. **Check ASGI configuration:**
   - Verify `ASGI_APPLICATION` in settings.py
   - Check `enhancefund/asgi.py` exists and is correct

3. **Check for import errors:**
   ```bash
   python manage.py check
   ```

## Debugging Steps

### Step 1: Check Server Logs

When you start Daphne, you should see:
```
INFO     Starting server at tcp:port=8000:interface=0.0.0.0
INFO     Listening on TCP address 0.0.0.0:8000
```

When WebSocket connects, you should see:
```
✅ WebSocket connected for user: user@email.com (ID: 123)
```

### Step 2: Test WebSocket Connection Manually

Open browser console and run:
```javascript
const token = 'YOUR_TOKEN_HERE';
const ws = new WebSocket(`ws://localhost:8000/ws/notifications/?token=${token}`);

ws.onopen = () => console.log('✅ Connected');
ws.onmessage = (e) => console.log('📨 Message:', JSON.parse(e.data));
ws.onerror = (e) => console.error('❌ Error:', e);
ws.onclose = (e) => console.log('🔌 Closed:', e.code, e.reason);
```

### Step 3: Check Database

```python
# Check if token exists
from rest_framework.authtoken.models import Token
Token.objects.filter(key='your_token').exists()

# Check if notifications are being created
from users.models import Notification
Notification.objects.count()
```

### Step 4: Test Notification Creation

```python
# Manually create a notification
from users.models import Notification, User
user = User.objects.get(email='your@email.com')
Notification.objects.create(
    user=user,
    notification_type='fund_added',
    title='Test Notification',
    message='This is a test'
)
```

## Quick Fixes

### Fix 1: Restart Server
```bash
# Stop current server (Ctrl+C)
# Start again
daphne -b 0.0.0.0 -p 8000 enhancefund.asgi:application
```

### Fix 2: Clear Channel Layer (if using Redis)
```bash
redis-cli FLUSHALL
```

### Fix 3: Check Token Format
- Frontend should use: `?token=TOKEN_KEY`
- NOT: `?token=Bearer TOKEN_KEY`
- NOT: `Authorization: Bearer TOKEN_KEY`

### Fix 4: Verify URL
- Correct: `ws://localhost:8000/ws/notifications/?token=...`
- Wrong: `ws://localhost:8000/api/ws/notifications/?token=...`
- Wrong: `ws://localhost:8000/notifications/?token=...`

## Testing Checklist

- [ ] Server running with Daphne
- [ ] Token exists in database
- [ ] User is active
- [ ] WebSocket URL is correct
- [ ] Token passed in query string
- [ ] No firewall blocking port 8000
- [ ] Browser console shows connection attempt
- [ ] Server logs show connection attempt

## Still Not Working?

1. **Check server terminal for error messages**
2. **Check browser console for detailed errors**
3. **Verify all files are saved and server restarted**
4. **Test with a simple WebSocket client tool**
5. **Check if port 8000 is already in use**

