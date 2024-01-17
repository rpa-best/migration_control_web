from django.urls import include, path
from rest_framework import routers
from v1_1.views.worker import WorkerAPIViewSet


router = routers.DefaultRouter()
router.register('worker', WorkerAPIViewSet, 'worker')

urlpatterns = [
    path('', include(router.urls)),
]