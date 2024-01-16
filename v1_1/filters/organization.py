import django_filters.rest_framework as filters
from v1_1.models import OrganizationUser


class OrganizationUserFilter(filters.FilterSet):
    role = filters.BaseInFilter('role')

    class Meta:
        model = OrganizationUser
        fields = ('role',)