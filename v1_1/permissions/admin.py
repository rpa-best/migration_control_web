from rest_framework.permissions import BasePermission
from v1_1.models.organization import OrganizationUser


class IsAdministrator(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated:
            # Проверяем, является ли пользователь администратором организации
            if OrganizationUser.objects.filter(user=request.user, role='admin').exists():
                # Получаем организацию, к которой относится объект
                organization = obj.organization
                # Получаем начальника/владельца организации
                owner = organization.owner
                # Проверяем, что у владельца подписка активна
                if owner.subscription_active:
                    return True
            else:
                return False
        return False