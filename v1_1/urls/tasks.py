from django.urls import include, path
from rest_framework import routers
from v1_1.views.tasks import ExpiringDocumentsView


router = routers.DefaultRouter()
router.register('list-task', ExpiringDocumentsView, 'list-task')

urlpatterns = [
    path('', include(router.urls)),
]