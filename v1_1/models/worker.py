from django.db import models
from v1_1.common_utils.file_paths import UploadPath
from v1_1.models.organization import Organization


class Worker(models.Model):
    GENDERS = (
        ('male', 'Male'),
        ('female', 'Female'),
    )

    name = models.CharField(max_length=150)
    surname = models.CharField(max_length=150)
    lastname = models.CharField(max_length=150, blank=True, null=True)
    gender = models.CharField(max_length=50, choices=GENDERS)
    citizenship = models.CharField(max_length=255, blank=True)
    birthday = models.DateField(blank=True, null=True)
    place_birth = models.CharField(max_length=255, blank=True)
    organization = models.ForeignKey('Organization', on_delete=models.CASCADE)
    phone = models.CharField(max_length=28, unique=True, blank=True, null=True,
                             default=None)
    registration_address = models.CharField(max_length=255, blank=True)
    email = models.EmailField(blank=True, null=True)
    avatar = models.ImageField(upload_to=UploadPath('image'), null=True)
    inn = models.CharField(max_length=20, unique=True, blank=True, null=True)
    processing_personal_data = models.BooleanField(default=0)



