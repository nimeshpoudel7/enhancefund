# Real-Time Notifications Setup Guide

## Overview

This system provides real-time notifications for various events in the EnhanceFund platform. Notifications are stored in the database and can be accessed via REST API or WebSocket.

## Events That Trigger Notifications

1. **Fund Added** - When user adds funds to wallet
2. **Fund Withdrawn** - When user withdraws funds
3. **Investment Made** - When investor makes an investment
4. **Investment Return** - When investment closes and returns are received
5. **Loan Funded** - When a loan receives funding (notifies borrower)
6. **Loan Fulfilled** - When a loan is fully funded (notifies borrower and investors)
7. **Loan Approved** - When a loan status changes to approved (notifies borrower)

## Setup Instructions

### Step 1: Run Migrations

```bash
python manage.py makemigrations users
python manage.py migrate
```

### Step 2: Verify Signals Are Registered

The signals are automatically registered when the app starts. Make sure `users.apps.UsersConfig` is in `INSTALLED_APPS` in `settings.py`.

### Step 3: Test Notifications

1. Add funds to your wallet
2. Make an investment
3. Check notifications via API: `GET /api/notifications/`

## API Endpoints

### Get All Notifications

```
GET /api/notifications/
Query Parameters:
  - is_read: true/false (optional, filter by read status)
  - type: notification_type (optional, filter by type)
```

**Response:**

```json
{
  "code": 1,
  "message": "Notifications retrieved successfully",
  "data": {
    "notifications": [
      {
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
    ],
    "unread_count": 5,
    "total_count": 10
  }
}
```

### Get Unread Count

```
GET /api/notifications/unread-count/
```

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

### Mark Notification as Read

```
PATCH /api/notifications/{id}/
Body: { "is_read": true }
```

### Mark All as Read

```
POST /api/notifications/mark-all-read/
```

### Get Single Notification

```
GET /api/notifications/{id}/
```

## Frontend Integration

### Option 1: Polling (Simple)

```javascript
// Poll for new notifications every 30 seconds
setInterval(async () => {
  const response = await fetch("/api/notifications/unread-count/", {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  const { data } = await response.json();

  // Update notification badge
  document.getElementById("notification-badge").textContent = data.unread_count;
}, 30000);

// Fetch notifications when notification icon is clicked
async function loadNotifications() {
  const response = await fetch("/api/notifications/?is_read=false", {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  const { data } = await response.json();
  displayNotifications(data.notifications);
}
```

### Option 2: WebSocket (Real-time) - Recommended

See WebSocket setup section below.

## WebSocket Setup (Django Channels)

### Step 1: Install Django Channels

```bash
pip install channels channels-redis
```

Add to `requirements.txt`:

```
channels==4.0.0
channels-redis==4.2.0
```

### Step 2: Update settings.py

```python
INSTALLED_APPS = [
    # ... existing apps ...
    'channels',
    'daphne',  # ASGI server
]

# Add at the end of settings.py
ASGI_APPLICATION = 'enhancefund.asgi.application'

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('127.0.0.1', 6379)],
        },
    },
}
```

### Step 3: Update asgi.py

```python
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import users.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'enhancefund.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            users.routing.websocket_urlpatterns
        )
    ),
})
```

### Step 4: Create WebSocket Consumer

Create `users/consumers.py`:

```python
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import Notification

User = get_user_model()

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        if self.user.is_authenticated:
            self.room_group_name = f"notifications_{self.user.id}"

            # Join room group
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )

            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            # Leave room group
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json.get('message', '')

    async def notification_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'notification': event['notification']
        }))
```

### Step 5: Create WebSocket Routing

Create `users/routing.py`:

```python
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/notifications/$', consumers.NotificationConsumer.as_asgi()),
]
```

### Step 6: Update Signals to Send WebSocket Messages

Update `users/signals.py` to include:

```python
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def send_notification_websocket(user_id, notification_data):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"notifications_{user_id}",
        {
            'type': 'notification_message',
            'notification': notification_data
        }
    )
```

Then call this function in each signal after creating the notification.

### Step 7: Run with Daphne

```bash
daphne -b 0.0.0.0 -p 8000 enhancefund.asgi:application
```

## Frontend WebSocket Integration

```javascript
// Connect to WebSocket
const token = localStorage.getItem("token");
const ws = new WebSocket(
  `ws://localhost:8000/ws/notifications/?token=${token}`
);

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.type === "notification") {
    // Show notification
    showNotification(data.notification);
    // Update badge count
    updateNotificationBadge();
  }
};

ws.onerror = (error) => {
  console.error("WebSocket error:", error);
};

ws.onclose = () => {
  // Reconnect after 5 seconds
  setTimeout(() => {
    connectWebSocket();
  }, 5000);
};
```

## Notification Types Reference

- `fund_added` - Fund Added
- `fund_withdrawn` - Fund Withdrawn
- `investment_made` - Investment Made
- `investment_return` - Investment Return
- `loan_funded` - Loan Funded
- `loan_fulfilled` - Loan Fulfilled
- `loan_approved` - Loan Approved

## Testing

1. Create a test user
2. Add funds → Should create `fund_added` notification
3. Make investment → Should create `investment_made` notification
4. Check API: `GET /api/notifications/`
5. Mark as read: `PATCH /api/notifications/{id}/`
6. Check unread count: `GET /api/notifications/unread-count/`

## Troubleshooting

1. **Notifications not created**: Check that signals are registered in `users/apps.py`
2. **WebSocket not connecting**: Verify Redis is running and Channels is configured
3. **Permission errors**: Ensure user is authenticated
