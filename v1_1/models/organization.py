from django.db import models
from v1_1.models.user import User


class Organization(models.Model):
    ORGANIZATIONAL_FORM = [
        ('1', 'ООО'),
        ('2', 'ПАО'),
        ('3', 'НАО'),
        ('4', 'ЗАО'),
        ('5', 'ИП'),
    ]

    organizational_form = models.CharField(choices=ORGANIZATIONAL_FORM, default='1', max_length=1)
    name = models.CharField(max_length=255, blank=True)
    inn = models.CharField(max_length=20, unique=True)
    kpp = models.CharField(max_length=9, blank=True, null=True)
    ogrn = models.CharField(max_length=13, blank=True, null=True)
    okved = models.CharField(max_length=10, blank=True, null=True)
    phone = models.CharField(max_length=28, unique=True, blank=True, null=True, default=None)
    owner = models.ForeignKey(User, models.CASCADE, blank=True, null=True)
    legal_address = models.CharField(max_length=255, blank=True)
    create_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_organizational_form_display()}"


class DirectorOrganization(models.Model):
    organization = models.OneToOneField(Organization, on_delete=models.CASCADE, unique=True)
    name_director = models.CharField(max_length=150)
    surname_director = models.CharField(max_length=150)
    patronymic_director = models.CharField(max_length=150, blank=True, null=True)
    passport_series = models.CharField(max_length=20, blank=True, null=True)
    passport_number = models.CharField(max_length=255, blank=True, null=True)
    issued_whom = models.CharField(max_length=150,  blank=True, null=True)
    date_issue_passport = models.DateField(blank=True, null=True)
    date_end_passport = models.DateField(blank=True, null=True)


class Bank(models.Model):
    organization_id = models.OneToOneField(Organization, on_delete=models.CASCADE, unique=True)
    bic = models.CharField(max_length=9, unique=True)
    correspondent_account = models.CharField(max_length=20)
    payment_account = models.CharField(max_length=20)

    class Meta:
        unique_together = ('organization_id', 'bic')


class OrganizationUser(models.Model):
    USER_ROLE_CHOICES = (
        ('owner', 'Владелец'),
        ('admin', 'Администратор'),
        ('observer', 'Зритель'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, to_field='username')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=USER_ROLE_CHOICES)

    class Meta:
        unique_together = ('user', 'organization')


class MigrationAddress(models.Model):
    organization = models.ForeignKey(Organization, models.CASCADE)
    name = models.CharField(max_length=255, blank=True)


class ResponsiblePersons(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    name = models.CharField(max_length=150)
    surname = models.CharField(max_length=150)
    patronymic = models.CharField(max_length=150, blank=True, null=True)
    passport_series = models.CharField(max_length=20, blank=True, null=True)
    passport_number = models.CharField(max_length=255, blank=True, null=True)
    issued_whom = models.CharField(max_length=150)
    date_issue_passport = models.DateField(blank=True, null=True)
    date_end_passport = models.DateField(blank=True, null=True)

