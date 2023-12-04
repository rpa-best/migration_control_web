from django.db import models
from v1_1.models.user import User


class BankInfo(models.Model):
    bank_id = models.CharField(max_length=9)
    correspondent_account = models.CharField(max_length=20)
    payment_account = models.CharField(max_length=20)


class Organization(models.Model):
    name = models.CharField(max_length=255, blank=True)
    organizational_form = models.CharField(max_length=255, blank=True)
    inn = models.CharField(max_length=20, unique=True)
    kpp = models.CharField(max_length=9, unique=True)
    ogrn = models.CharField(max_length=13, blank=True)
    kpp = models.CharField(max_length=20, blank=True)
    owner_id = models.ForeignKey(User, models.CASCADE)
    bank_info_id = models.ForeignKey(BankInfo, models.PROTECT)
    legal_address = models.CharField(max_length=255, blank=True)
    create_at = models.DateTimeField(auto_now=True)
    balance = models.FloatField(default=0)


class OrganizationUser(models.Model):
    USER_ROLE_CHOICES = (
        ('owner', 'Owner'),
        ('admin', 'Administrator'),
        ('observer', 'Observer'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=USER_ROLE_CHOICES)

    class Meta:
        unique_together = ('user', 'organization')