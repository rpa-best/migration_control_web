from django.urls import include, path
from rest_framework import routers
from v1_1.views.organization import OrganizationAPIViewSet, MigrationAddressAPIViewSet, OrganizationUsersListView
from v1_1.views.worker import WorkerAPIViewSet

router = routers.DefaultRouter()
router.register('organization', OrganizationAPIViewSet, 'organization')
router.register('migration_address', MigrationAddressAPIViewSet, 'migration_address')
router.register('worker', WorkerAPIViewSet, 'worker')
router.register(r'(?P<organization>\d+)/list-users', OrganizationUsersListView, 'list-users'),

urlpatterns = [
    path('', include(router.urls)),
]