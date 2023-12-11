from rest_framework.permissions import BasePermission
from v1_1.models.organization import OrganizationUser


class IsObserver(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated and OrganizationUser.objects.filter(user=request.user, role='observer').exists():
            return True
        return False