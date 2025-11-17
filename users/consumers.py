import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token

User = get_user_model()


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """Handle WebSocket connection"""
        try:
            # User should be set by TokenAuthMiddleware
            self.user = self.scope.get("user")
            path = self.scope.get("path", "N/A")
            
            print(f"🔍 Consumer connect called - Path: {path}, User: {self.user}")
            
            # Check if user exists and is authenticated
            # Django's User model has is_authenticated as a property
            if self.user and (hasattr(self.user, 'is_authenticated') and self.user.is_authenticated):
                self.room_group_name = f"notifications_{self.user.id}"
                
                # Accept connection first
                await self.accept()
                
                # Join room group
                await self.channel_layer.group_add(
                    self.room_group_name,
                    self.channel_name
                )
                
                # Send connection confirmation
                await self.send(text_data=json.dumps({
                    'type': 'connection',
                    'message': 'Connected to notifications',
                    'user_id': self.user.id
                }))
                print(f"✅ WebSocket connected for user: {self.user.email} (ID: {self.user.id})")
            else:
                print(f"❌ WebSocket connection rejected: User not authenticated. User: {self.user}, Type: {type(self.user)}")
                if self.user is None:
                    print(f"   → User is None - check token authentication in middleware")
                elif not hasattr(self.user, 'is_authenticated'):
                    print(f"   → User object doesn't have is_authenticated attribute")
                elif not self.user.is_authenticated:
                    print(f"   → User is not authenticated")
                # Accept first, then close with proper code
                await self.accept()
                await self.close(code=4001)  # Unauthorized
        except Exception as e:
            print(f"❌ Error in WebSocket connect: {str(e)}")
            import traceback
            traceback.print_exc()
            try:
                await self.accept()
                await self.close(code=4000)  # Internal error
            except:
                pass  # Connection already closed

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        try:
            if hasattr(self, 'room_group_name'):
                # Leave room group
                await self.channel_layer.group_discard(
                    self.room_group_name,
                    self.channel_name
                )
            user_info = self.user.email if hasattr(self, 'user') and self.user else 'Unknown'
            print(f"🔌 WebSocket disconnected for user: {user_info} (Code: {close_code})")
        except Exception as e:
            print(f"⚠️ Error during disconnect: {str(e)}")
            # Don't raise - disconnect should always succeed

    async def receive(self, text_data):
        """Handle messages received from WebSocket"""
        try:
            text_data_json = json.loads(text_data)
            message_type = text_data_json.get('type', '')
            
            if message_type == 'ping':
                # Respond to ping with pong
                await self.send(text_data=json.dumps({
                    'type': 'pong',
                    'message': 'pong'
                }))
        except json.JSONDecodeError:
            pass

    async def notification_message(self, event):
        """Send notification message to WebSocket"""
        try:
            notification = event['notification']
            await self.send(text_data=json.dumps({
                'type': 'notification',
                'notification': notification
            }))
        except Exception as e:
            print(f"⚠️ Error sending notification message: {str(e)}")
            # If connection is broken, disconnect gracefully
            if "Broken pipe" in str(e) or "Connection closed" in str(e):
                await self.close(code=1000)

    async def unread_count_update(self, event):
        """Send unread count update to WebSocket"""
        try:
            await self.send(text_data=json.dumps({
                'type': 'unread_count',
                'unread_count': event['unread_count']
            }))
        except Exception as e:
            print(f"⚠️ Error sending unread count update: {str(e)}")
            # If connection is broken, disconnect gracefully
            if "Broken pipe" in str(e) or "Connection closed" in str(e):
                await self.close(code=1000)

    @database_sync_to_async
    def get_user_from_token(self, token_key):
        """Get user from token"""
        try:
            token = Token.objects.get(key=token_key)
            return token.user
        except Token.DoesNotExist:
            return None


