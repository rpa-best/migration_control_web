import secrets
import string
from django.core.mail import send_mail
from django.conf import settings


def send_sms(phone, pvc):
    pass


def get_random_integer(number):
    return ''.join(secrets.choice(string.digits) for _ in range(number))


def send_email(email, title, text):
    send_mail(title, text, settings.EMAIL_HOST_USER, [email])
