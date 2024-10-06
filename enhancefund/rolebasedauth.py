from rest_framework import permissions
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from enhancefund.permissions import IsAuthenticatedAndInGroup


class BaseAuthenticatedView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

class BaseBorrowerView(BaseAuthenticatedView):
    permission_classes = [IsAuthenticated, IsAuthenticatedAndInGroup(['Borrower'])]

    def get_permissions(self):
        return [IsAuthenticated(), IsAuthenticatedAndInGroup(['Borrower'])]

class BaseInvestorView(BaseAuthenticatedView):
    permission_classes = [IsAuthenticated, IsAuthenticatedAndInGroup(['Investor'])]

    def get_permissions(self):
        return [IsAuthenticated(), IsAuthenticatedAndInGroup(['Investor'])]

class BaseStaffView(BaseAuthenticatedView):
    permission_classes = [IsAuthenticated, IsAuthenticatedAndInGroup(['Staff'])]

    def get_permissions(self):
        return [IsAuthenticated(), IsAuthenticatedAndInGroup(['Staff'])]

class BaseAllRolesView(BaseAuthenticatedView):
    permission_classes = [IsAuthenticated, IsAuthenticatedAndInGroup(['Borrower', 'Investor', 'Staff'])]

    def get_permissions(self):
        return [IsAuthenticated(), IsAuthenticatedAndInGroup(['Borrower', 'Investor', 'Staff'])]