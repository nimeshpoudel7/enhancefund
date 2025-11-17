from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q

from enhancefund.utils import enhance_response
from enhancefund.rolebasedauth import BaseAuthenticatedView
from enhancefund.postvalidators import BaseValidator
from .models import Notification
from .serializers import NotificationSerializer


class NotificationListView(BaseAuthenticatedView, BaseValidator, generics.ListAPIView):
    """
    Get all notifications for the authenticated user
    """
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        queryset = Notification.objects.filter(user=user)
        
        # Filter by read/unread status if provided
        is_read = self.request.query_params.get('is_read', None)
        if is_read is not None:
            is_read_bool = is_read.lower() == 'true'
            queryset = queryset.filter(is_read=is_read_bool)
        
        # Filter by notification type if provided
        notification_type = self.request.query_params.get('type', None)
        if notification_type:
            queryset = queryset.filter(notification_type=notification_type)
        
        return queryset.order_by('-created_at')
    
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        
        # Get unread count
        unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
        
        return enhance_response(
            data={
                'notifications': serializer.data,
                'unread_count': unread_count,
                'total_count': queryset.count()
            },
            message="Notifications retrieved successfully",
            status=status.HTTP_200_OK
        )


class NotificationDetailView(BaseAuthenticatedView, BaseValidator, generics.RetrieveUpdateAPIView):
    """
    Get or update a specific notification (mark as read)
    """
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)
    
    def patch(self, request, *args, **kwargs):
        notification = self.get_object()
        is_read = request.data.get('is_read', None)
        
        if is_read is not None:
            notification.is_read = bool(is_read)
            notification.save()
        
        serializer = self.get_serializer(notification)
        return enhance_response(
            data=serializer.data,
            message="Notification updated successfully",
            status=status.HTTP_200_OK
        )


class MarkAllNotificationsReadView(BaseAuthenticatedView, BaseValidator, generics.GenericAPIView):
    """
    Mark all notifications as read for the authenticated user
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        updated_count = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).update(is_read=True)
        
        return enhance_response(
            data={'marked_read_count': updated_count},
            message=f"Marked {updated_count} notifications as read",
            status=status.HTTP_200_OK
        )


class NotificationUnreadCountView(BaseAuthenticatedView, BaseValidator, generics.GenericAPIView):
    """
    Get unread notification count
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
        
        return enhance_response(
            data={'unread_count': unread_count},
            message="Unread count retrieved successfully",
            status=status.HTTP_200_OK
        )


