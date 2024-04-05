from django.urls import include, path
from rest_framework import routers
from v1_1.views.organization import (OrganizationAPIViewSet, ShowMigrationAddressAPIViewSet, MigrationAddressAPIViewSet,
                                     OrganizationUsersListView, SearchOrganizationAPIViewSet,
                                     ShowResponsiblePersonsAPIViewSet, ResponsiblePersonsAPIViewSet,
                                     ShowBodiesMIAAPIViewSet, BodiesMIAAPIViewSet, SearchBankAPIViewSet,
                                     BankShowAndCreateAPIViewSet, BankUpdateAPIViewSet)


router = routers.DefaultRouter()
router.register('organization', OrganizationAPIViewSet, 'organization')
router.register(r'(?P<inn_or_ogrn>\d+)/search-organization', SearchOrganizationAPIViewSet, 'search-organization'),
router.register(r'(?P<organization>\d+)/migration-address', ShowMigrationAddressAPIViewSet, 'list-migration-address')
router.register('migration-address', MigrationAddressAPIViewSet, 'migration-address')
router.register(r'(?P<organization>\d+)/users', OrganizationUsersListView, 'organization-users'),
router.register(r'(?P<organization>\d+)/responsible-persons', ShowResponsiblePersonsAPIViewSet, 'responsible-persons')
router.register('responsible-persons', ResponsiblePersonsAPIViewSet, 'responsible-persons')
router.register(r'(?P<organization>\d+)/bodies-mia', ShowBodiesMIAAPIViewSet, 'bodies-mi')
router.register('bodies-mia', BodiesMIAAPIViewSet, 'bodies-mia')
router.register(r'(?P<bik>\d+)/search-bank', SearchBankAPIViewSet, 'search-bank'),
router.register(r'(?P<organization>\d+)/bank', BankShowAndCreateAPIViewSet, 'bank-show-and-create')
router.register('bank', BankUpdateAPIViewSet, 'bank-update')

urlpatterns = [
    path('', include(router.urls)),
]