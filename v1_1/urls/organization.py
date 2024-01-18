from django.urls import include, path
from rest_framework import routers
from v1_1.views.organization import OrganizationAPIViewSet, MigrationAddressAPIViewSet, OrganizationUsersListView


router = routers.DefaultRouter()
router.register('organization', OrganizationAPIViewSet, 'organization')
router.register('migration-address', MigrationAddressAPIViewSet, 'migration-address')
router.register(r'(?P<organization>\d+)/users', OrganizationUsersListView, 'organization-users'),

urlpatterns = [
    path('', include(router.urls)),
]