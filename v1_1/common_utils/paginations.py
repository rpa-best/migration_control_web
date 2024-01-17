from collections import OrderedDict
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response


class CustomPagination(LimitOffsetPagination):

    def paginate_queryset(self, queryset, request, view=None):
        self.view = view
        self.limit = self.get_limit(request)
        # if self.limit is None:
        #     return None

        self.count = self.get_count(queryset)
        self.offset = self.get_offset(request)
        self.request = request
        # if self.count > self.limit and self.template is not None:
        #     self.display_page_controls = True

        if self.count == 0 or self.offset > self.count:
            return []
        if self.limit is None:
            return queryset
        return list(queryset[self.offset:self.offset + self.limit])

    def get_paginated_response(self, data):
        headers = self.view.default_response_headers
        permissions = headers.get("Has-Permissions", [])
        if self.limit is None:
            return Response(OrderedDict([
                ('count', self.count),
                ('next', None),
                ('next_offset', None),
                ('previous_offset', None),
                ('previous', None),
                ('results', data)
            ]))
        next_offset = self.offset + self.limit
        previous_offset = self.offset - self.limit
        return Response(OrderedDict([
            ('count', self.count),
            ('next', self.get_next_link()),
            ('next_offset', next_offset if next_offset < self.count else None),
            ('previous_offset', previous_offset if previous_offset > 0 else None),
            ('previous', self.get_previous_link()),
            ('results', data)
        ]))

    def get_paginated_response_schema(self, schema):
        return {
            'type': 'object',
            'properties': {
                'count': {
                  'type': 'integer',
                  'example': 123,
                },
                'next': {
                    'type': 'string',
                    'nullable': True,
                    'format': 'uri',
                    'example': 'https://api.example.org/accounts/?limit=10&offset=30'
                },
                'previous': {
                  'type': 'string',
                  'nullable': True,
                  'format': 'uri',
                  'example': 'https://api.example.org/accounts/?limit=10&offset=10'
                },
                'next_offset': {
                    'type': 'integer',
                    'example': 30
                },
                'previous_offset': {
                    'type': 'integer',
                    'example': 10,
                },
                'results': schema
            }
        }