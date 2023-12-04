from django.conf import settings
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.backends import TokenBackend
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import RefreshToken as _RefreshToken
from rest_framework_simplejwt.utils import datetime_from_epoch
from v1_1.common_utils import get_client_ip
from v1_1.models.user import UserOutstandingToken


# This code is responsible for generating tokens for authenticating users in the application. It uses \
# the rest_framework_simplejwt library to work with JWT tokens and the UserOutstandingToken model to store \
# information about issued tokens.

class RefreshToken(_RefreshToken):

    # The method generates a token for a specific user.
    @classmethod
    def for_user(cls, user, request=None):
        user_id = getattr(user, api_settings.USER_ID_FIELD)
        if not isinstance(user_id, int):
            user_id = str(user_id)

        token = cls()
        token[api_settings.USER_ID_CLAIM] = user_id

        device_id = 0
        user_ip = None
        user_agent = None
        if request:
            # Getting information about the request: IP address, user - agent and device id.
            device_id = int(request.META.get('HTTP_X_DEVICE_ID', 0))
            user_ip = get_client_ip(request)
            user_agent = request.META['HTTP_USER_AGENT']

        UserOutstandingToken.objects.create(
            user=user,
            jti=token[api_settings.JTI_CLAIM],
            token=str(token),
            created_at=token.current_time,
            expires_at=datetime_from_epoch(token['exp']),
            device_id=device_id,
            ip_address=user_ip,
            mac_address=None,
            user_agent=user_agent,
            user_id=user_id
        )
        return token


# A class for generating tokens for client authentication, so it defines parameters for signing and verifying the token.
class ClientRefreshToken(RefreshToken):
    _token_backend = TokenBackend(
        api_settings.ALGORITHM,
        settings.CLIENT_SIGNING_KEY,  # api_settings.SIGNING_KEY,
        api_settings.VERIFYING_KEY,
        api_settings.AUDIENCE,
        api_settings.ISSUER,
        api_settings.JWK_URL,
        api_settings.LEEWAY,
        api_settings.JSON_ENCODER,
    )


# The function is used to determine the token class depending on the type of authentication (regular or client-side).
def get_token_class(request):
    try:
        JWTAuthentication().authenticate(request)
        return ClientRefreshToken
    except InvalidToken:
        return RefreshToken

# The function is used to generate a token for a specific user and request.
def get_token(request, user):
    return get_token_class(request).for_user(user, request)

