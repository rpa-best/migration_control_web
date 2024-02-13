from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView
from migration_control_web.settings import SPECTACULAR_ACCOUNT_SETTINGS, SPECTACULAR_ORGANIZATION_SETTINGS, \
    SPECTACULAR_WORKER_SETTINGS, SPECTACULAR_BLANKS_SETTINGS, SPECTACULAR_TASKS_SETTINGS
from v1_1.swagger_content import SpectacularSwaggerView

urlpatterns = [
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='docs'),
    path('schema-account/', SpectacularAPIView.as_view(custom_settings=SPECTACULAR_ACCOUNT_SETTINGS),
         name='schema_account'),
    path('schema-organization/', SpectacularAPIView.as_view(custom_settings=SPECTACULAR_ORGANIZATION_SETTINGS),
         name='schema_organization'),
    path('schema-worker/', SpectacularAPIView.as_view(custom_settings=SPECTACULAR_WORKER_SETTINGS),
         name='schema_worker'),
    path('schema-blanks/', SpectacularAPIView.as_view(custom_settings=SPECTACULAR_BLANKS_SETTINGS),
         name='schema_blanks'),
    path('schema-tasks/', SpectacularAPIView.as_view(custom_settings=SPECTACULAR_TASKS_SETTINGS),
         name='schema_tasks'),
    path('account/', include('v1_1.urls.account')),
    path('organization/', include('v1_1.urls.organization')),
    path('worker/', include('v1_1.urls.worker')),
    path('blanks/', include('v1_1.urls.blanks')),
    path('tasks/', include('v1_1.urls.tasks'))
]