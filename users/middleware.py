from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from urllib.parse import parse_qs

User = get_user_model()


class TokenAuthMiddleware(BaseMiddleware):
    """
    Custom middleware to authenticate WebSocket connections using token
    """
    
    def __init__(self, inner):
        super().__init__(inner)
    
    async def __call__(self, scope, receive, send):
        # Only process WebSocket connections
        if scope['type'] == 'websocket':
            # Get token from query string
            query_string = scope.get('query_string', b'').decode()
            token_key = None
            
            print(f"🔍 WebSocket connection attempt - Path: {scope.get('path', 'N/A')}, Query: {query_string}")
            
            if query_string:
                try:
                    # Parse query string
                    params = parse_qs(query_string)
                    token_list = params.get('token', [])
                    if token_list:
                        token_key = token_list[0]
                        print(f"🔑 Token extracted: {token_key[:10]}...")
                except Exception as e:
                    print(f"❌ Error parsing query string: {e}")
            
            # Authenticate user
            if token_key:
                scope['user'] = await self.get_user_from_token(token_key)
            else:
                print(f"⚠️ No token provided in query string")
                scope['user'] = None
        
        return await super().__call__(scope, receive, send)
    
    @database_sync_to_async
    def get_user_from_token(self, token_key):
        """Get user from token"""
        try:
            if not token_key:
                return None
            token = Token.objects.select_related('user').get(key=token_key)
            user = token.user
            # Ensure user is active
            if user and user.is_active:
                print(f"✅ Token authenticated for user: {user.email} (ID: {user.id})")
                return user
            print(f"❌ User is not active: {user.email if user else 'None'}")
            return None
        except Token.DoesNotExist:
            print(f"❌ Token not found: {token_key[:10] if token_key else 'None'}...")
            return None
        except Exception as e:
            print(f"❌ Error getting user from token: {e}")
            import traceback
            traceback.print_exc()
            return None

