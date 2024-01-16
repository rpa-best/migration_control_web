from rest_framework.permissions import BasePermission
from v1_1.models.organization import OrganizationUser
from v1_1.models.subscription import Subscription


# class IsAdministrator(BasePermission):
#     def has_permission(self, request, view):
#         organization = request.data.get('organization')
#         print(organization)
#         if request.user.is_authenticated:
#             # Проверяем, является ли пользователь администратором организации
#             if OrganizationUser.objects.filter(user=request.user, organization=organization, role='admin').exists():
#                 # Получение владельца организации
#                 owner = OrganizationUser.objects.filter(organization=organization, role='owner').first()
#                 # Проверка на активную подписку владельца
#                 if Subscription.objects.filter(user=owner, status='active').exists():
#                     return True
#         return False
#
#     def has_object_permission(self, request, view, obj):
#         return self.has_permission(request, view)


class IsAdministratorInOrganization(BasePermission):
    def has_permission(self, request, view):
        organization = request.data.get('organization')
        print(organization)
        if request.user.is_authenticated:
            # Проверяем, является ли пользователь администратором организации
            if OrganizationUser.objects.filter(user=request.user, organization=organization, role='admin').exists():
                # Получение владельца организации
                owner = OrganizationUser.objects.filter(organization=organization, role='owner').first()
                # Проверка на активную подписку владельца
                if Subscription.objects.filter(user=owner, status='active').exists():
                    return True
        return False

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)