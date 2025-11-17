# Real-Time Notifications - Frontend Integration Contract

## Overview

Complete working implementation for real-time notifications using WebSocket and REST API.

## Installation

### Install Required Packages

```bash
npm install  # No additional packages needed - uses native WebSocket API
```

## WebSocket Connection

### Connection URL

```
ws://localhost:8000/ws/notifications/?token=YOUR_AUTH_TOKEN
```

### Authentication

- Pass authentication token as query parameter: `?token=YOUR_TOKEN`
- Token is the same token used for REST API authentication

## Complete React Component Example

```jsx
import React, { useState, useEffect, useRef, useCallback } from "react";

const NotificationSystem = () => {
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [isConnected, setIsConnected] = useState(false);
  const [showNotifications, setShowNotifications] = useState(false);
  const wsRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);
  const API_BASE_URL = "http://localhost:8000/api";
  const WS_URL = "ws://localhost:8000/ws/notifications";

  // Get auth token (adjust based on your auth implementation)
  const getToken = () => {
    return localStorage.getItem("token") || sessionStorage.getItem("token");
  };

  // Connect to WebSocket
  const connectWebSocket = useCallback(() => {
    const token = getToken();
    if (!token) {
      console.error("No authentication token found");
      return;
    }

    try {
      const ws = new WebSocket(`${WS_URL}/?token=${token}`);

      ws.onopen = () => {
        console.log("WebSocket connected");
        setIsConnected(true);
        // Clear any pending reconnection
        if (reconnectTimeoutRef.current) {
          clearTimeout(reconnectTimeoutRef.current);
        }
      };

      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);

        if (data.type === "connection") {
          console.log("WebSocket connection confirmed:", data.message);
        } else if (data.type === "notification") {
          // New notification received
          const newNotification = data.notification;
          setNotifications((prev) => [newNotification, ...prev]);
          setUnreadCount((prev) => prev + 1);

          // Show browser notification if permission granted
          if (
            "Notification" in window &&
            Notification.permission === "granted"
          ) {
            new Notification(newNotification.title, {
              body: newNotification.message,
              icon: "/notification-icon.png",
            });
          }
        } else if (data.type === "unread_count") {
          // Unread count update
          setUnreadCount(data.unread_count);
        } else if (data.type === "pong") {
          // Heartbeat response
          console.log("WebSocket heartbeat received");
        }
      };

      ws.onerror = (error) => {
        console.error("WebSocket error:", error);
        setIsConnected(false);
      };

      ws.onclose = () => {
        console.log("WebSocket disconnected");
        setIsConnected(false);

        // Reconnect after 5 seconds
        reconnectTimeoutRef.current = setTimeout(() => {
          connectWebSocket();
        }, 5000);
      };

      wsRef.current = ws;
    } catch (error) {
      console.error("Error connecting to WebSocket:", error);
      setIsConnected(false);
    }
  }, []);

  // Disconnect WebSocket
  const disconnectWebSocket = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
  }, []);

  // Send ping to keep connection alive
  const sendPing = useCallback(() => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type: "ping" }));
    }
  }, []);

  // Fetch notifications from API
  const fetchNotifications = useCallback(async (isRead = null) => {
    try {
      const token = getToken();
      let url = `${API_BASE_URL}/notifications/`;
      if (isRead !== null) {
        url += `?is_read=${isRead}`;
      }

      const response = await fetch(url, {
        headers: {
          Authorization: `Token ${token}`,
          "Content-Type": "application/json",
        },
      });

      const result = await response.json();
      if (result.code === 1) {
        setNotifications(result.data.notifications);
        setUnreadCount(result.data.unread_count);
      }
    } catch (error) {
      console.error("Error fetching notifications:", error);
    }
  }, []);

  // Mark notification as read
  const markAsRead = useCallback(async (notificationId) => {
    try {
      const token = getToken();
      const response = await fetch(
        `${API_BASE_URL}/notifications/${notificationId}/`,
        {
          method: "PATCH",
          headers: {
            Authorization: `Token ${token}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ is_read: true }),
        }
      );

      const result = await response.json();
      if (result.code === 1) {
        setNotifications((prev) =>
          prev.map((notif) =>
            notif.id === notificationId ? { ...notif, is_read: true } : notif
          )
        );
        setUnreadCount((prev) => Math.max(0, prev - 1));
      }
    } catch (error) {
      console.error("Error marking notification as read:", error);
    }
  }, []);

  // Mark all as read
  const markAllAsRead = useCallback(async () => {
    try {
      const token = getToken();
      const response = await fetch(
        `${API_BASE_URL}/notifications/mark-all-read/`,
        {
          method: "POST",
          headers: {
            Authorization: `Token ${token}`,
            "Content-Type": "application/json",
          },
        }
      );

      const result = await response.json();
      if (result.code === 1) {
        setNotifications((prev) =>
          prev.map((notif) => ({ ...notif, is_read: true }))
        );
        setUnreadCount(0);
      }
    } catch (error) {
      console.error("Error marking all as read:", error);
    }
  }, []);

  // Request browser notification permission
  const requestNotificationPermission = useCallback(() => {
    if ("Notification" in window && Notification.permission === "default") {
      Notification.requestPermission();
    }
  }, []);

  // Initialize
  useEffect(() => {
    // Request notification permission
    requestNotificationPermission();

    // Fetch initial notifications
    fetchNotifications();

    // Connect to WebSocket
    connectWebSocket();

    // Send ping every 30 seconds to keep connection alive
    const pingInterval = setInterval(sendPing, 30000);

    return () => {
      disconnectWebSocket();
      clearInterval(pingInterval);
    };
  }, [
    connectWebSocket,
    disconnectWebSocket,
    fetchNotifications,
    sendPing,
    requestNotificationPermission,
  ]);

  // Format date
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return "Just now";
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString();
  };

  // Get notification icon based on type
  const getNotificationIcon = (type) => {
    const icons = {
      fund_added: "💰",
      fund_withdrawn: "💸",
      investment_made: "📈",
      investment_return: "🎉",
      loan_funded: "💵",
      loan_fulfilled: "✅",
      loan_approved: "🎊",
    };
    return icons[type] || "🔔";
  };

  return (
    <div className="notification-container">
      {/* Notification Bell Icon */}
      <div
        className="notification-icon-wrapper"
        onClick={() => setShowNotifications(!showNotifications)}
      >
        <svg
          width="24"
          height="24"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
        >
          <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" />
          <path d="M13.73 21a2 2 0 0 1-3.46 0" />
        </svg>
        {unreadCount > 0 && (
          <span className="notification-badge">
            {unreadCount > 99 ? "99+" : unreadCount}
          </span>
        )}
        {!isConnected && (
          <span className="connection-indicator" title="Disconnected">
            ⚠️
          </span>
        )}
      </div>

      {/* Notifications Dropdown */}
      {showNotifications && (
        <div className="notifications-dropdown">
          <div className="notifications-header">
            <h3>Notifications</h3>
            {unreadCount > 0 && (
              <button onClick={markAllAsRead} className="mark-all-read-btn">
                Mark all as read
              </button>
            )}
          </div>

          <div className="notifications-list">
            {notifications.length === 0 ? (
              <div className="no-notifications">No notifications</div>
            ) : (
              notifications.map((notification) => (
                <div
                  key={notification.id}
                  className={`notification-item ${
                    !notification.is_read ? "unread" : ""
                  }`}
                  onClick={() =>
                    !notification.is_read && markAsRead(notification.id)
                  }
                >
                  <div className="notification-icon">
                    {getNotificationIcon(notification.notification_type)}
                  </div>
                  <div className="notification-content">
                    <div className="notification-title">
                      {notification.title}
                    </div>
                    <div className="notification-message">
                      {notification.message}
                    </div>
                    <div className="notification-time">
                      {formatDate(notification.created_at)}
                    </div>
                  </div>
                  {!notification.is_read && <div className="unread-dot"></div>}
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default NotificationSystem;
```

## CSS Styles

```css
.notification-container {
  position: relative;
  display: inline-block;
}

.notification-icon-wrapper {
  position: relative;
  cursor: pointer;
  padding: 8px;
  border-radius: 50%;
  transition: background-color 0.2s;
}

.notification-icon-wrapper:hover {
  background-color: #f0f0f0;
}

.notification-badge {
  position: absolute;
  top: 0;
  right: 0;
  background-color: #ff4444;
  color: white;
  border-radius: 10px;
  padding: 2px 6px;
  font-size: 12px;
  font-weight: bold;
  min-width: 18px;
  text-align: center;
}

.connection-indicator {
  position: absolute;
  bottom: 0;
  right: 0;
  font-size: 10px;
}

.notifications-dropdown {
  position: absolute;
  top: 100%;
  right: 0;
  width: 400px;
  max-height: 600px;
  background: white;
  border: 1px solid #ddd;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 1000;
  margin-top: 8px;
}

.notifications-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid #eee;
}

.notifications-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.mark-all-read-btn {
  background: none;
  border: none;
  color: #007bff;
  cursor: pointer;
  font-size: 14px;
  padding: 4px 8px;
}

.mark-all-read-btn:hover {
  text-decoration: underline;
}

.notifications-list {
  max-height: 500px;
  overflow-y: auto;
}

.notification-item {
  display: flex;
  padding: 12px 16px;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
  transition: background-color 0.2s;
  position: relative;
}

.notification-item:hover {
  background-color: #f8f9fa;
}

.notification-item.unread {
  background-color: #f0f7ff;
}

.notification-icon {
  font-size: 24px;
  margin-right: 12px;
  flex-shrink: 0;
}

.notification-content {
  flex: 1;
  min-width: 0;
}

.notification-title {
  font-weight: 600;
  font-size: 14px;
  margin-bottom: 4px;
  color: #333;
}

.notification-message {
  font-size: 13px;
  color: #666;
  margin-bottom: 4px;
  line-height: 1.4;
}

.notification-time {
  font-size: 11px;
  color: #999;
}

.unread-dot {
  width: 8px;
  height: 8px;
  background-color: #007bff;
  border-radius: 50%;
  margin-left: 8px;
  flex-shrink: 0;
  align-self: center;
}

.no-notifications {
  padding: 40px;
  text-align: center;
  color: #999;
}

/* Scrollbar styling */
.notifications-list::-webkit-scrollbar {
  width: 6px;
}

.notifications-list::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.notifications-list::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 3px;
}

.notifications-list::-webkit-scrollbar-thumb:hover {
  background: #555;
}
```

## Vanilla JavaScript Example

```javascript
class NotificationManager {
  constructor(apiBaseUrl, wsUrl, token) {
    this.apiBaseUrl = apiBaseUrl || "http://localhost:8000/api";
    this.wsUrl = wsUrl || "ws://localhost:8000/ws/notifications";
    this.token = token;
    this.ws = null;
    this.reconnectTimeout = null;
    this.callbacks = {
      onNotification: null,
      onUnreadCount: null,
      onConnectionChange: null,
    };
  }

  connect() {
    if (!this.token) {
      console.error("No token provided");
      return;
    }

    try {
      this.ws = new WebSocket(`${this.wsUrl}/?token=${this.token}`);

      this.ws.onopen = () => {
        console.log("WebSocket connected");
        if (this.callbacks.onConnectionChange) {
          this.callbacks.onConnectionChange(true);
        }
      };

      this.ws.onmessage = (event) => {
        const data = JSON.parse(event.data);

        if (data.type === "notification") {
          if (this.callbacks.onNotification) {
            this.callbacks.onNotification(data.notification);
          }
        } else if (data.type === "unread_count") {
          if (this.callbacks.onUnreadCount) {
            this.callbacks.onUnreadCount(data.unread_count);
          }
        }
      };

      this.ws.onerror = (error) => {
        console.error("WebSocket error:", error);
      };

      this.ws.onclose = () => {
        console.log("WebSocket disconnected");
        if (this.callbacks.onConnectionChange) {
          this.callbacks.onConnectionChange(false);
        }
        // Reconnect after 5 seconds
        this.reconnectTimeout = setTimeout(() => this.connect(), 5000);
      };
    } catch (error) {
      console.error("Error connecting:", error);
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout);
    }
  }

  async fetchNotifications(isRead = null) {
    let url = `${this.apiBaseUrl}/notifications/`;
    if (isRead !== null) {
      url += `?is_read=${isRead}`;
    }

    const response = await fetch(url, {
      headers: {
        Authorization: `Token ${this.token}`,
        "Content-Type": "application/json",
      },
    });

    const result = await response.json();
    return result.code === 1 ? result.data : null;
  }

  async markAsRead(notificationId) {
    const response = await fetch(
      `${this.apiBaseUrl}/notifications/${notificationId}/`,
      {
        method: "PATCH",
        headers: {
          Authorization: `Token ${this.token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ is_read: true }),
      }
    );

    const result = await response.json();
    return result.code === 1;
  }

  async markAllAsRead() {
    const response = await fetch(
      `${this.apiBaseUrl}/notifications/mark-all-read/`,
      {
        method: "POST",
        headers: {
          Authorization: `Token ${this.token}`,
          "Content-Type": "application/json",
        },
      }
    );

    const result = await response.json();
    return result.code === 1;
  }

  on(event, callback) {
    if (
      this.callbacks.hasOwnProperty(
        `on${event.charAt(0).toUpperCase() + event.slice(1)}`
      )
    ) {
      this.callbacks[`on${event.charAt(0).toUpperCase() + event.slice(1)}`] =
        callback;
    }
  }
}

// Usage
const token = localStorage.getItem("token");
const notificationManager = new NotificationManager(
  "http://localhost:8000/api",
  "ws://localhost:8000/ws/notifications",
  token
);

notificationManager.on("notification", (notification) => {
  console.log("New notification:", notification);
  // Update UI
});

notificationManager.on("unreadCount", (count) => {
  console.log("Unread count:", count);
  // Update badge
});

notificationManager.connect();
```

## API Contract

### WebSocket Messages

#### Client → Server

```json
{
  "type": "ping"
}
```

#### Server → Client

**Connection Confirmation:**

```json
{
  "type": "connection",
  "message": "Connected to notifications",
  "user_id": 123
}
```

**New Notification:**

```json
{
  "type": "notification",
  "notification": {
    "id": 1,
    "notification_type": "fund_added",
    "notification_type_display": "Fund Added",
    "title": "Fund Added Successfully",
    "message": "Your wallet has been credited with $100.00...",
    "is_read": false,
    "created_at": "2024-01-15T10:30:00Z",
    "related_id": 123,
    "related_type": "transaction"
  }
}
```

**Unread Count Update:**

```json
{
  "type": "unread_count",
  "unread_count": 5
}
```

**Pong (Heartbeat Response):**

```json
{
  "type": "pong",
  "message": "pong"
}
```

## REST API Endpoints

### GET /api/notifications/

Get all notifications

**Query Parameters:**

- `is_read` (optional): `true` or `false`
- `type` (optional): notification type

**Response:**

```json
{
  "code": 1,
  "message": "Notifications retrieved successfully",
  "data": {
    "notifications": [...],
    "unread_count": 5,
    "total_count": 10
  }
}
```

### GET /api/notifications/unread-count/

Get unread notification count

**Response:**

```json
{
  "code": 1,
  "message": "Unread count retrieved successfully",
  "data": {
    "unread_count": 5
  }
}
```

### PATCH /api/notifications/{id}/

Mark notification as read

**Body:**

```json
{
  "is_read": true
}
```

### POST /api/notifications/mark-all-read/

Mark all notifications as read

**Response:**

```json
{
  "code": 1,
  "message": "Marked 5 notifications as read",
  "data": {
    "marked_read_count": 5
  }
}
```

## Notification Types

| Type                | Display Name      | Description                          |
| ------------------- | ----------------- | ------------------------------------ |
| `fund_added`        | Fund Added        | When user adds funds to wallet       |
| `fund_withdrawn`    | Fund Withdrawn    | When user withdraws funds            |
| `investment_made`   | Investment Made   | When investor makes an investment    |
| `investment_return` | Investment Return | When investment closes with returns  |
| `loan_funded`       | Loan Funded       | When loan receives funding           |
| `loan_fulfilled`    | Loan Fulfilled    | When loan is fully funded            |
| `loan_approved`     | Loan Approved     | When loan status changes to approved |

## Testing

1. **Start Django server with Daphne:**

   ```bash
   daphne -b 0.0.0.0 -p 8000 enhancefund.asgi:application
   ```

2. **Test WebSocket connection:**

   ```javascript
   const ws = new WebSocket(
     "ws://localhost:8000/ws/notifications/?token=YOUR_TOKEN"
   );
   ws.onopen = () => console.log("Connected");
   ws.onmessage = (e) => console.log("Message:", JSON.parse(e.data));
   ```

3. **Trigger notification:**
   - Add funds to wallet
   - Make an investment
   - Check WebSocket receives notification

## Production Considerations

1. **Use Redis for Channel Layers:**

   ```python
   CHANNEL_LAYERS = {
       'default': {
           'BACKEND': 'channels_redis.core.RedisChannelLayer',
           'CONFIG': {
               "hosts": [('127.0.0.1', 6379)],
           },
       },
   }
   ```

2. **Use WSS (Secure WebSocket) in production:**

   ```
   wss://yourdomain.com/ws/notifications/?token=YOUR_TOKEN
   ```

3. **Add reconnection logic with exponential backoff**

4. **Handle token refresh for long-lived connections**

5. **Add rate limiting for WebSocket connections**
