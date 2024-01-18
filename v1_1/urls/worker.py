from django.urls import include, path
from rest_framework import routers
from v1_1.views.worker import WorkerAPIViewSet, DocumentsWorkerAPIViewSet


router = routers.DefaultRouter()
router.register('worker', WorkerAPIViewSet, 'worker')
router.register(r'(?P<worker_id>\d+)/document', DocumentsWorkerAPIViewSet, 'worker-documents'),


urlpatterns = [
    path('', include(router.urls)),
]