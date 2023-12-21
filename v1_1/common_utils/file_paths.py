import os
import uuid
from pathlib import Path
from django.core.files.storage import default_storage
from django.db.models import F


# Класс, позволяющий сгенерировать путь для сохранения файла
class UploadPath:

    def __init__(self, folder_name, file_name_from='pk', hashing=True):
        self.folder_name = folder_name
        self.file_name_from = file_name_from
        self.hashing = hashing
        super(UploadPath, self).__init__()

    # Метод генерирует путь для сохранения файла, используя переданные аргументы
    def __call__(self, instance, filename):
        ext = Path(filename).suffix
        filename = uuid.uuid4()
        filename = f'{filename}{ext}'
        folder_name = self.folder_name
        if isinstance(self.folder_name, F):
            folder_name = getattr(instance, self.folder_name.name)
        return str(Path(instance.__class__.__name__, folder_name, filename))

    # Метод позволяет сериализовать объект класса UploadPath для использования в миграциях.
    def deconstruct(self):
        return f'{self.__module__}.{self.__class__.__name__}', [self.folder_name], {}


# Функция принимает относительный URL и возвращает абсолютный URL для доступа к файлу. Она также заменяет протокол https
# значением переменной окружения AWS_S3_ENDPOINT_URL, чтобы получить правильный URL для доступа к файлу на сервере S3.
def get_absolute_media_url(releted_url):
    return f"{os.getenv('AWS_S3_ENDPOINT_URL')}/{releted_url}"

# Функция принимает поле модели ImageField и возвращает абсолютный URL-адрес для доступа к файлу
def get_absolute_media_url_from_field(field):
    return default_storage.url(field)