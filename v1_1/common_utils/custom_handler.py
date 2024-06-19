from rest_framework import status
from rest_framework.exceptions import APIException, _get_error_details
from django.utils.translation import gettext_lazy as _


class CustomValidationError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _('Invalid input.')
    default_code = 'invalid'

    def __init__(self, detail=None, code=None):
        if detail is None:
            detail = self.default_detail
        if code is None:
            code = self.default_code

        # В случае сбоев при проверке собирается множество ошибок вместе,
        # поэтому данные всегда следует приводить к списку, если это еще не сделано.
        if isinstance(detail, tuple):
            detail = list(detail)
        elif not isinstance(detail, dict) and not isinstance(detail, list):
            detail = [detail]

        self.detail = _get_error_details(detail, code)