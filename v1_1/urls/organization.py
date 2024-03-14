from django.urls import include, path
from rest_framework import routers
from v1_1.views.organization import (OrganizationAPIViewSet, ShowMigrationAddressAPIViewSet, MigrationAddressAPIViewSet,
                                     OrganizationUsersListView, SearchOrganizationAPIViewSet)


router = routers.DefaultRouter()
router.register('organization', OrganizationAPIViewSet, 'organization')
router.register(r'(?P<inn_or_ogrn>\d+)/search-organization', SearchOrganizationAPIViewSet, 'search-organization'),
router.register(r'(?P<organization>\d+)/migration-address', ShowMigrationAddressAPIViewSet, 'list-migration-address')
router.register('migration-address', MigrationAddressAPIViewSet, 'migration-address')
router.register(r'(?P<organization>\d+)/users', OrganizationUsersListView, 'organization-users'),

urlpatterns = [
    path('', include(router.urls)),
]