from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view, inline_serializer


blanks = extend_schema_view(
    post=extend_schema(
        tags=['Blanks']
    )
)

organization_search = extend_schema_view(
    post=extend_schema(
        tags=['Blanks']
    )
)

search_worker = extend_schema_view(
    list=extend_schema(
        tags=['Search worker']
    )
)