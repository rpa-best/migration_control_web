import django_filters.rest_framework as filters
from v1_1.models import OrganizationUser


class OrganizationUserFilter(filters.FilterSet):
    # id = filters.BaseInFilter()
    organization_id = filters.BaseInFilter('organization_id')

    class Meta:
        model = OrganizationUser
        fields = ('organization_id',)