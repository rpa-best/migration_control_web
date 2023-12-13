from django.urls import include, path
from rest_framework import routers
from v1_1.views.organization import OrganizationAPIViewSet, MigrationAddressAPIViewSet


router = routers.DefaultRouter()
router.register('organization', OrganizationAPIViewSet, 'organization')
router.register('migration_address', MigrationAddressAPIViewSet, 'migration_address')


urlpatterns = [
    path('', include(router.urls)),
]