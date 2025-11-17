# Testing WebSocket with Postman

## Prerequisites

- Postman version 8.0 or later (WebSocket support was added in v8.0)
- Your Django server running with Daphne
- Your authentication token

## Steps to Connect

### 1. Open Postman and Create New Request

1. Open Postman
2. Click **"New"** button (top left)
3. Select **"WebSocket Request"** (or search for "WebSocket" in the template gallery)

### 2. Enter WebSocket URL

Enter your WebSocket URL with the token as a query parameter:

```
ws://127.0.0.1:8000/ws/notifications/?token=YOUR_TOKEN_HERE
```

**Example:**

```
ws://127.0.0.1:8000/ws/notifications/?token=aec8e0e9a0b3d8637b8926a5adffb44e487330ec
```

### 3. Connect

1. Click the **"Connect"** button
2. You should see:
   - Connection status: **Connected**
   - Server response showing connection confirmation:
     ```json
     {
       "type": "connection",
       "message": "Connected to notifications",
       "user_id": 56
     }
     ```

### 4. Send Test Messages

#### Send Ping (Keep-Alive)

In the message input at the bottom, type:

```json
{ "type": "ping" }
```

Click **"Send"**

You should receive a pong response:

```json
{
  "type": "pong",
  "message": "pong"
}
```

### 5. Monitor Messages

Postman will show:

- **Messages** tab: All messages sent and received
- **Connection** status: Shows if connected/disconnected
- **Timestamps**: When each message was sent/received

## Expected Behavior

### On Connection

You should see:

```json
{
  "type": "connection",
  "message": "Connected to notifications",
  "user_id": 56
}
```

### On Ping

Send:

```json
{ "type": "ping" }
```

Receive:

```json
{
  "type": "pong",
  "message": "pong"
}
```

### On Notification

When a notification is triggered (e.g., fund added, investment made), you'll receive:

```json
{
  "type": "notification",
  "notification": {
    "id": 1,
    "notification_type": "fund_added",
    "notification_type_display": "Fund Added",
    "title": "Fund Added Successfully",
    "message": "Your fund of $1000.00 has been added successfully.",
    "is_read": false,
    "created_at": "2025-11-17T15:00:00Z",
    "related_id": 123,
    "related_type": "transaction"
  }
}
```

### On Unread Count Update

You'll receive:

```json
{
  "type": "unread_count",
  "unread_count": 5
}
```

## Troubleshooting

### Connection Fails

1. **Check server is running:**

   ```bash
   daphne -b 0.0.0.0 -p 8000 enhancefund.asgi:application
   ```

2. **Check token is valid:**

   - Make sure you're using a valid authentication token
   - Token should match the one used in REST API calls

3. **Check URL format:**
   - Must start with `ws://` (not `http://`)
   - Token must be in query string: `?token=YOUR_TOKEN`

### Connection Closes Immediately

1. **Check server logs** - Look for authentication errors
2. **Verify token** - Token might be invalid or expired
3. **Check user is active** - User account must be active

### No Messages Received

1. **Send a ping** to test the connection
2. **Trigger a notification** by:
   - Adding funds via API
   - Making an investment
   - Any action that triggers notifications

## Testing Notification Flow

### Step 1: Connect WebSocket in Postman

Connect to:

```
ws://127.0.0.1:8000/ws/notifications/?token=YOUR_TOKEN
```

### Step 2: Trigger a Notification

In another Postman tab (or curl), make a request that triggers a notification:

**Add Fund:**

```bash
POST http://127.0.0.1:8000/api/investor/add-fund/
Authorization: Token YOUR_TOKEN
Content-Type: application/json

{
  "amount": 1000.00
}
```

### Step 3: See Notification in WebSocket

You should immediately see the notification appear in your WebSocket connection in Postman.

## Postman WebSocket Features

### Message History

- All sent/received messages are saved
- You can see the full conversation history

### Auto-Reconnect

- Postman can auto-reconnect if connection drops
- Enable in connection settings

### Save Requests

- Save WebSocket connections as collections
- Reuse for future testing

## Alternative: Using Browser Console

If Postman doesn't work, you can also test in browser console:

```javascript
const token = "YOUR_TOKEN_HERE";
const ws = new WebSocket(
  `ws://127.0.0.1:8000/ws/notifications/?token=${token}`
);

ws.onopen = () => {
  console.log("✅ Connected");
};

ws.onmessage = (e) => {
  console.log("📨 Received:", JSON.parse(e.data));
};

ws.onclose = (e) => {
  console.log("🔌 Closed:", e.code, e.reason);
};

ws.onerror = (e) => {
  console.error("❌ Error:", e);
};

// Send ping
ws.send(JSON.stringify({ type: "ping" }));
```

## Quick Test Checklist

- [ ] Postman version 8.0+
- [ ] Server running with Daphne
- [ ] Valid authentication token
- [ ] Correct WebSocket URL format
- [ ] Connection successful
- [ ] Ping/pong working
- [ ] Notifications received when triggered

## Notes

- **Postman WebSocket** is great for testing and debugging
- **Browser console** is useful for quick tests
- **Frontend integration** should use the React/Vanilla JS examples from the frontend contract

If you're still having connection issues, check:

1. Server logs for errors
2. Token validity
3. User account status
4. Network/firewall settings
