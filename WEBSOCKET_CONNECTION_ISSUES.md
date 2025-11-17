# WebSocket Connection Issues - Disconnecting After 2 Seconds

## Problem

WebSocket connects successfully but disconnects after ~2 seconds.

## Possible Causes

### 1. Frontend Closing Connection

The frontend might be closing the connection intentionally or due to an error.

**Check your frontend code:**

- Look for `ws.close()` calls
- Check if there's error handling that closes the connection
- Verify reconnection logic isn't causing issues

### 2. No Keep-Alive/Ping

If there's no activity, some proxies/firewalls close idle connections.

**Solution:** The frontend should send ping messages every 30 seconds:

```javascript
// Send ping every 30 seconds
setInterval(() => {
  if (ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify({ type: "ping" }));
  }
}, 30000);
```

### 3. Browser Tab/Window Issues

- Browser might be suspending the tab
- Page navigation might close the connection

### 4. Network/Proxy Issues

- Firewall closing idle connections
- Proxy timeout

## Debugging Steps

### Step 1: Check Frontend Connection Code

Make sure your frontend has proper error handling:

```javascript
const ws = new WebSocket(
  `ws://127.0.0.1:8000/ws/notifications/?token=${token}`
);

ws.onopen = () => {
  console.log("✅ Connected");
  // Start ping interval
  const pingInterval = setInterval(() => {
    if (ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ type: "ping" }));
    } else {
      clearInterval(pingInterval);
    }
  }, 30000);
};

ws.onclose = (event) => {
  console.log("🔌 Disconnected:", event.code, event.reason);
  // Reconnect after 5 seconds
  setTimeout(() => {
    connectWebSocket();
  }, 5000);
};

ws.onerror = (error) => {
  console.error("❌ Error:", error);
};
```

### Step 2: Check Server Logs

The server logs show:

- `✅ WebSocket connected` - Connection successful
- `🔌 WebSocket disconnected` - Connection closed

Check the close code:

- `1000` = Normal closure
- `1001` = Going away
- `1006` = Abnormal closure (no close frame)
- `4001` = Unauthorized

### Step 3: Test with Simple Client

Test with a simple WebSocket client to isolate the issue:

```javascript
// In browser console
const token = "aec8e0e9a0b3d8637b8926a5adffb44e487330ec";
const ws = new WebSocket(
  `ws://127.0.0.1:8000/ws/notifications/?token=${token}`
);

ws.onopen = () => {
  console.log("✅ Connected");
  // Keep connection alive
  setInterval(() => {
    if (ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ type: "ping" }));
      console.log("📤 Sent ping");
    }
  }, 30000);
};

ws.onmessage = (e) => {
  console.log("📨 Received:", JSON.parse(e.data));
};

ws.onclose = (e) => {
  console.log("🔌 Closed:", e.code, e.reason, "Clean:", e.wasClean);
};

ws.onerror = (e) => {
  console.error("❌ Error:", e);
};
```

## Solutions

### Solution 1: Add Keep-Alive in Frontend

Make sure your frontend sends ping messages:

```javascript
// In your React hook or component
useEffect(() => {
  if (ws && ws.readyState === WebSocket.OPEN) {
    const pingInterval = setInterval(() => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ type: "ping" }));
      }
    }, 30000);

    return () => clearInterval(pingInterval);
  }
}, [ws]);
```

### Solution 2: Check for Errors in Frontend

Look for any code that might be closing the connection:

- Error handlers that call `ws.close()`
- Component unmounting
- Navigation events

### Solution 3: Add Reconnection Logic

```javascript
let reconnectAttempts = 0;
const maxReconnectAttempts = 5;

function connectWebSocket() {
  const ws = new WebSocket(
    `ws://127.0.0.1:8000/ws/notifications/?token=${token}`
  );

  ws.onopen = () => {
    console.log("✅ Connected");
    reconnectAttempts = 0; // Reset on successful connection
  };

  ws.onclose = (event) => {
    console.log("🔌 Disconnected:", event.code);
    if (reconnectAttempts < maxReconnectAttempts) {
      reconnectAttempts++;
      setTimeout(() => {
        console.log(`🔄 Reconnecting (attempt ${reconnectAttempts})...`);
        connectWebSocket();
      }, 5000);
    }
  };

  return ws;
}
```

## Common Close Codes

- **1000** - Normal closure (intentional close)
- **1001** - Going away (page navigation, tab close)
- **1006** - Abnormal closure (network issue, no close frame)
- **4001** - Unauthorized (authentication failed)

## Next Steps

1. **Check your frontend code** - Look for `ws.close()` calls
2. **Add ping/keep-alive** - Send ping every 30 seconds
3. **Check browser console** - Look for errors or close events
4. **Monitor server logs** - See the close code and reason

The connection is working (it connects successfully), so the issue is likely in the frontend closing it or a timeout. Check your frontend WebSocket code!
