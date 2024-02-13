from drf_spectacular.plumbing import set_query_parameters
from drf_spectacular.settings import spectacular_settings
from drf_spectacular.utils import extend_schema
from drf_spectacular.views import SpectacularSwaggerView as _SpectacularSwaggerView
from rest_framework.response import Response


SERVIES_SCHEMA_URLS = {
    'Migration control Account': '/api/v1.1/schema-account/',
    'Migration control Organization': '/api/v1.1/schema-organization/',
    'Migration control Worker': '/api/v1.1/schema-worker/',
    'Migration control Blanks': '/api/v1.1/schema-blanks/',
    'Migration control Tasks': '/api/v1.1/schema-tasks/',
}


class SpectacularSwaggerView(_SpectacularSwaggerView):
    template_name = 'drf-spectacular/custom_swagger_ui.html'

    @extend_schema(exclude=True)
    def get(self, request, *args, **kwargs):
        return Response(
            data={
                'services': SERVIES_SCHEMA_URLS.keys(),
                'title': 'Swagger Migration control',
                'dist': self._swagger_ui_dist(),
                'favicon_href': self._swagger_ui_favicon(),
                'schema_url': self._get_schema_url(request),
                'settings': self._dump(spectacular_settings.SWAGGER_UI_SETTINGS),
                'oauth2_config': self._dump(spectacular_settings.SWAGGER_UI_OAUTH2_CONFIG),
                'template_name_js': self.template_name_js,
                'csrf_header_name': self._get_csrf_header_name(),
                'schema_auth_names': self._dump(self._get_schema_auth_names()),
            },
            template_name=self.template_name,
        )

    def _get_schema_url(self, request):
        host = f"{request.scheme}://{request.get_host()}"
        return set_query_parameters(
            url=f"{host}{SERVIES_SCHEMA_URLS.get(self.request.query_params.get('service', 'Migration control Account'))}",
            lang=request.GET.get('lang'),
            version=request.GET.get('version')
        )