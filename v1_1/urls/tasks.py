from django.urls import include, path
from rest_framework import routers
from v1_1.views.tasks import ExpiringDocumentsView, WorkerExpiringDocumentsView, ShowNumberTasksView


router = routers.DefaultRouter()
router.register('list', ExpiringDocumentsView, 'list-task')
router.register(r'(?P<worker_id>\d+)/list', WorkerExpiringDocumentsView, 'worker-tasks'),
router.register('number', ShowNumberTasksView, 'number')

urlpatterns = [
    path('', include(router.urls)),
]