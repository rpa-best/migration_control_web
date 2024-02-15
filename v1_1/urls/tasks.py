from django.urls import include, path
from rest_framework import routers
from v1_1.views.tasks import ExpiringDocumentsView, TaskInfoView


router = routers.DefaultRouter()
router.register('list', ExpiringDocumentsView, 'list-task')
router.register(r'info/(?P<document_id>\d+)', TaskInfoView, 'task-info')

urlpatterns = [
    path('', include(router.urls)),
]