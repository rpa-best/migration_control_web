from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view, inline_serializer
from rest_framework import serializers
from v1_1.serializers.account import AccountCreateSerializer


auth = extend_schema_view(
    post=extend_schema(
        tags=['sign in and sign up'],
        request=inline_serializer('auth_request', {
            'username': serializers.CharField(),
            'password': serializers.CharField()
        }),
        responses={
            '200': inline_serializer('auth_response2', {
                'access': serializers.CharField(),
                'refresh': serializers.CharField()
            })
        }
    )
)


create = extend_schema_view(
    post=extend_schema(
        tags=['sign in and sign up'],
        responses={
            '200': inline_serializer('user_create_response', {
                'access': serializers.CharField(),
                'refresh': serializers.CharField(),
                'user': AccountCreateSerializer()
            })
        }
    )
)


refresh = extend_schema_view(
    post=extend_schema(
        tags=['sign in and sign up']
    )
)


account = extend_schema_view(
    get=extend_schema(
        tags=['account']
    ),
    patch=extend_schema(
        tags=['account']
    ),
    put=extend_schema(
        tags=['account']
    )
)

change_password = extend_schema_view(
    post=extend_schema(
        tags=['account'],
    )
)