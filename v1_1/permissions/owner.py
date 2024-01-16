from rest_framework.permissions import BasePermission
from v1_1.models import OrganizationUser
from v1_1.models.subscription import Subscription


class IsOwner(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated and Subscription.objects.filter(user=request.user, status='active').exists():
            return True
        return False

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class IsnOwnerInOrganization(BasePermission):
    def has_permission(self, request, view):
        organization = request.data.get('organization')
        if request.user.is_authenticated:
            # Проверяем, является ли пользователь владельцем организации
            if OrganizationUser.objects.filter(user=request.user, organization=organization, role='owner').exists():
                # Проверка на активную подписку владельца
                if Subscription.objects.filter(user=request.user, status='active').exists():
                    return True
        return False

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)