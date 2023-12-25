from rest_framework.permissions import BasePermission
from v1_1.models.subscription import Subscription


class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated and Subscription.objects.filter(user=request.user, status='active').exists():
            return True
        return False