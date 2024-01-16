from drf_spectacular.openapi import AutoSchema
from drf_spectacular.plumbing import is_basic_type, is_serializer
from drf_spectacular.utils import OpenApiExample, OpenApiParameter, OpenApiResponse, inline_serializer
from rest_framework import serializers
from rest_framework.permissions import AllowAny


error_serializer = inline_serializer(name='error_serializer',
                                     many=False,
                                     fields={'field': serializers.CharField()})

class CustomAutoSchema(AutoSchema):
    common_response = {'400': OpenApiResponse(response=error_serializer,
                                              description='Ошибка валидации',
                                              ),
                       '401': OpenApiResponse(response=error_serializer,
                                              description='Требуется авторизация, либо ошибка авторизации',
                                              ),
                       '403': OpenApiResponse(response=error_serializer,
                                              description='Нет разрешения на выполнение данной операции',
                                              )}

    def _get_response_bodies(self, direction='response'):
        response_serializers = self.get_response_serializers()
        common_response = self.common_response.copy()
        if self.view.permission_classes == [AllowAny]:
            del common_response['401']
            del common_response['403']
        if (
                is_serializer(response_serializers)
                or is_basic_type(response_serializers)
                or isinstance(response_serializers, OpenApiResponse)
        ):
            if self.method == 'DELETE':
                to_parse = {'200': OpenApiResponse(response=error_serializer,
                                                   examples=[
                                                       OpenApiExample('custom delete',
                                                                      value={'message': 'удаление прошло успешно'},
                                                                      response_only=True,
                                                                      status_codes=[200]
                                                                      )
                                                   ]
                                                   )}
            elif self._is_create_operation():
                to_parse = {'201': response_serializers}
            else:
                to_parse = {'200': response_serializers}
            common_response.update(to_parse)
        elif isinstance(response_serializers, dict):
            common_response.update(response_serializers)
        responses = {}
        for code, serializer in common_response.items():
            if isinstance(code, tuple):
                code, media_types = str(code[0]), code[1:]
            else:
                code, media_types = str(code), None
            content_response = self._get_response_for_code(serializer, code, media_types, direction)
            if code in responses:
                responses[code]['content'].update(content_response['content'])
            else:
                responses[code] = content_response
        return responses

    def _get_parameters(self):
        parameters = super(CustomAutoSchema, self)._get_parameters()
        return parameters