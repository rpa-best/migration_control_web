import django_filters.rest_framework as filters
from v1_1.models.worker import Worker


class WorkerFilter(filters.FilterSet):
    status = filters.BaseInFilter('status')

    class Meta:
        model = Worker
        fields = ('status',)