from django.urls import include, path
from rest_framework import routers
from v1_1.views.worker import CreateAndUpdateWorkerAPIViewSet, DocumentsWorkerAPIViewSet, ShowWorkersAPIViewSet

router = routers.DefaultRouter()
router.register('worker', CreateAndUpdateWorkerAPIViewSet, 'worker')
router.register(r'(?P<organization>\d+)/worker', ShowWorkersAPIViewSet, 'list-worker')
router.register(r'(?P<worker_id>\d+)/document', DocumentsWorkerAPIViewSet, 'worker-documents'),


urlpatterns = [
    path('', include(router.urls)),
]