from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view, inline_serializer


blanks = extend_schema_view(
    post=extend_schema(
        tags=['Blanks']
    )
)