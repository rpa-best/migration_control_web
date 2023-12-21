from rest_framework.permissions import BasePermission

from v1_1.models.subscription import Subscription


class IsOwner(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated and Subscription.objects.filter(user=request.user, status='active').first():
            return True
        return False