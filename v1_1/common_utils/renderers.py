from rest_framework.renderers import BaseRenderer
from django.http import FileResponse
from django.http import HttpResponse
import zipfile
from collections import OrderedDict
import requests


class FileRenderer(BaseRenderer):
    media_type = 'application/zip'
    format = 'zip'

    def render(self, data, media_type=None, renderer_context=None):
        # Создаем объект HttpResponse с типом media_type
        response = HttpResponse(content_type=self.media_type)
        response['Content-Disposition'] = 'attachment; filename="archive.zip"'
        # Создаем zip-архив
        with zipfile.ZipFile(response, 'w') as zip_file:
            for result in data:
                file_name = result.split('/')[-1]
                file_name = file_name.replace(':', '_')  # Заменяем ":" на "_"
                file_content = requests.get(result).content
                zip_file.writestr(file_name, file_content)

        return response