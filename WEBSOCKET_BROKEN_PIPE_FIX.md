# WebSocket "Broken Pipe" Error - Fix Guide

## What is "Broken Pipe"?

A "Broken pipe" error occurs when:
- The client (browser/Postman) closes the connection unexpectedly
- The server tries to send data to a closed connection
- Network interruption during transmission

## Common Causes

### 1. Client Closes Connection
- Browser tab closed
- Page navigation
- Network interruption
- Client-side error closing the connection

### 2. Server Tries to Send to Closed Connection
- Notification sent after client disconnected
- Unread count update sent to closed connection

### 3. Network Issues
- Unstable network connection
- Firewall/proxy closing idle connections
- Timeout issues

## Fixes Applied

### 1. Better Error Handling
Added try-catch blocks around all `send()` operations to gracefully handle broken connections.

### 2. Graceful Disconnection
The disconnect handler now properly handles errors and doesn't raise exceptions.

### 3. Connection State Checking
Before sending messages, the code now checks if the connection is still open.

## Testing

### Test 1: Normal Connection
1. Connect to WebSocket
2. Keep connection open
3. Send ping
4. Should receive pong
5. Close connection normally
6. Should see clean disconnect log

### Test 2: Abrupt Disconnection
1. Connect to WebSocket
2. Close browser tab or Postman connection abruptly
3. Server should log disconnect without errors
4. "Broken pipe" should be handled gracefully

### Test 3: Send After Disconnect
1. Connect to WebSocket
2. Disconnect client
3. Trigger a notification (add funds, etc.)
4. Server should handle the error gracefully
5. No crash or unhandled exception

## What You Should See

### Normal Disconnect
```
🔌 WebSocket disconnected for user: sandra.investor@gmail.com (Code: 1000)
```

### Broken Pipe (Now Handled)
```
⚠️ Error sending notification message: Broken pipe
🔌 WebSocket disconnected for user: sandra.investor@gmail.com (Code: 1000)
```

## If You Still See Issues

### Check 1: Is Connection Actually Working?
Test with the Python script:
```bash
python test_websocket.py
```

### Check 2: Browser Console
Open browser console and check for errors:
```javascript
const ws = new WebSocket('ws://127.0.0.1:8000/ws/notifications/?token=YOUR_TOKEN');
ws.onerror = (e) => console.error('Error:', e);
ws.onclose = (e) => console.log('Closed:', e.code, e.reason);
```

### Check 3: Server Logs
Look for:
- Connection successful messages
- Any error messages
- Disconnect messages with close codes

## Close Codes Reference

- **1000** - Normal closure (intentional close)
- **1001** - Going away (page navigation, tab close)
- **1006** - Abnormal closure (network issue, no close frame)
- **4001** - Unauthorized (authentication failed)

## Best Practices

### Frontend
1. **Handle errors gracefully:**
   ```javascript
   ws.onerror = (error) => {
     console.error('WebSocket error:', error);
     // Reconnect logic here
   };
   ```

2. **Close connection properly:**
   ```javascript
   // Before page unload
   window.addEventListener('beforeunload', () => {
     if (ws && ws.readyState === WebSocket.OPEN) {
       ws.close(1000, 'Page closing');
     }
   });
   ```

3. **Reconnect on disconnect:**
   ```javascript
   ws.onclose = (event) => {
     if (event.code !== 1000) { // Not a normal close
       setTimeout(() => {
         connectWebSocket(); // Reconnect
       }, 5000);
     }
   };
   ```

### Backend
- All send operations are now wrapped in try-catch
- Disconnect handler handles errors gracefully
- Broken pipe errors are caught and logged, not raised

## Summary

The "Broken pipe" error is now handled gracefully. It's a normal part of WebSocket connections when clients disconnect unexpectedly. The server will:
1. Catch the error
2. Log it as a warning
3. Clean up the connection
4. Continue operating normally

This is **not a critical error** - it's just the server detecting that a client disconnected.

