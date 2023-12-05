from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from migration_control_web.settings import SPECTACULAR_ACCOUNT_SETTINGS
from v1_1.swagger_content import SpectacularSwaggerView

urlpatterns = [
    # path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='docs'),
    path('schema-account/', SpectacularAPIView.as_view(custom_settings=SPECTACULAR_ACCOUNT_SETTINGS),
         name='schema_account'),
    path('account/', include('v1_1.urls.account')),
]