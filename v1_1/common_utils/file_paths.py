import os
import uuid
from pathlib import Path
from django.core.files.storage import default_storage
from django.db.models import F


# A class that allows to generate a path to save a file
class UploadPath:

    def __init__(self, folder_name, file_name_from='pk', hashing=True):
        self.folder_name = folder_name
        self.file_name_from = file_name_from
        self.hashing = hashing
        super(UploadPath, self).__init__()

    # The method generates a path to save the file using the passed arguments
    def __call__(self, instance, filename):
        ext = Path(filename).suffix
        filename = uuid.uuid4()
        filename = f'{filename}{ext}'
        folder_name = self.folder_name
        if isinstance(self.folder_name, F):
            folder_name = getattr(instance, self.folder_name.name)
        return str(Path(instance.__class__.__name__, folder_name, filename))

    # The method allows you to serialize an object of the UploadPath class for use in migrations.
    def deconstruct(self):
        return f'{self.__module__}.{self.__class__.__name__}', [self.folder_name], {}


# The function takes a relative URL and returns an absolute URL to access the file. It also replaces the https protocol
# with the value of the AWS_S3_ENDPOINT_URL environment variable, to get the correct URL to access the file
# on the S3 server.
def get_absolute_media_url(releted_url):
    return f"{os.getenv('AWS_S3_ENDPOINT_URL')}/{releted_url}"

# The function takes the ImageField model field and returns the absolute URL for accessing the file,
def get_absolute_media_url_from_field(field):
    return default_storage.url(field)