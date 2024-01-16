from django.urls import include, path
from rest_framework import routers
from v1_1.views.organization import OrganizationUsersListView


router = routers.DefaultRouter()
router.register('list-users', OrganizationUsersListView, '')

urlpatterns = [
    path('', include(router.urls)),
]