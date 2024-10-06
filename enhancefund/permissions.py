from rest_framework import permissions

from rest_framework.views import exception_handler
from rest_framework.exceptions import AuthenticationFailed, NotAuthenticated, PermissionDenied
from rest_framework import status
from .utils import enhance_response

def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    # Now add the HTTP status code to the response.
    if response is not None:
        if isinstance(exc, (AuthenticationFailed, NotAuthenticated)):
            (print(exc))
            return enhance_response(
                data={},
                message=str(exc),
                status=status.HTTP_401_UNAUTHORIZED
            )

    return response

class IsAuthenticatedAndInGroup(permissions.BasePermission):
    message = 'You do not have permission to perform this action.'

    def __init__(self, allowed_groups):
        self.allowed_groups = allowed_groups

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            raise NotAuthenticated('Authentication required. Please log in.')

        if request.user.is_staff:
            return True

        if not request.user.groups.filter(name__in=self.allowed_groups).exists():
            raise PermissionDenied(f'Access denied. Your role does not have permission to perform this action. Required roles: {", ".join(self.allowed_groups)}')

        return True