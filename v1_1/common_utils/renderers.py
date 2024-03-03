from rest_pandas import PandasExcelRenderer as _PandasExcelRenderer
from rest_framework.renderers import BaseRenderer


class PandasExcelRenderer(_PandasExcelRenderer):
    def get_pandas_kwargs(self, data, renderer_context):
        return {
            "index": False
        }


class XMLRender(BaseRenderer):
    format = "xml"
    media_type = "application/xml"

    def render(self, data, accepted_media_type=None, renderer_context=None):
        return data