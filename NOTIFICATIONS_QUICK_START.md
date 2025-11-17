# Notifications Quick Start Guide

## What's Included

✅ **Notification Model** - Stores all notifications in database  
✅ **Django Signals** - Automatically creates notifications on events  
✅ **REST API Endpoints** - Get, read, and manage notifications  
✅ **Real-time Support** - Ready for WebSocket integration  

## Quick Setup (5 minutes)

### 1. Run Migrations
```bash
python manage.py makemigrations users
python manage.py migrate
```

### 2. Test It
1. Add funds to your wallet → Notification created automatically
2. Check notifications: `GET /api/notifications/`
3. See unread count: `GET /api/notifications/unread-count/`

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/notifications/` | GET | Get all notifications |
| `/api/notifications/unread-count/` | GET | Get unread count |
| `/api/notifications/mark-all-read/` | POST | Mark all as read |
| `/api/notifications/{id}/` | GET/PATCH | Get/Update notification |

## Frontend Integration (Simple Polling)

```javascript
// Update notification badge every 30 seconds
setInterval(async () => {
  const res = await fetch('/api/notifications/unread-count/', {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  const { data } = await res.json();
  document.getElementById('badge').textContent = data.unread_count;
}, 30000);

// Load notifications when icon clicked
async function showNotifications() {
  const res = await fetch('/api/notifications/?is_read=false', {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  const { data } = await res.json();
  // Display notifications
}
```

## Notification Events

- ✅ **Fund Added** - When wallet is credited
- ✅ **Fund Withdrawn** - When withdrawal is processed
- ✅ **Investment Made** - When investor invests
- ✅ **Investment Return** - When investment closes with returns
- ✅ **Loan Funded** - When loan receives funding (borrower notified)
- ✅ **Loan Fulfilled** - When loan is fully funded (all parties notified)
- ✅ **Loan Approved** - When loan status changes to approved

## Next Steps

For **real-time WebSocket** support, see `REALTIME_NOTIFICATIONS_SETUP.md`


