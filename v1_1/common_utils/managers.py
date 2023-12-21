from django.apps import apps
from django.contrib.auth.models import UserManager
from django.db.models import QuerySet
from django.db.models.expressions import RawSQL
from django.db.models.fields.related_descriptors import ForwardManyToOneDescriptor
from django.db.models.manager import BaseManager


def get_manager(*names):
    MANAGERS = {
        'filter_recursive': RecursionFindQuerySetMixin,
    }
    qs_list = [value for key, value in MANAGERS.items() if key in names]

    class QS(QuerySet, *qs_list):
        pass

    class Manager(BaseManager.from_queryset(QS)):
        pass

    if 'user' in names:
        class Manager(Manager, UserManager):
            use_in_migrations = False
            pass
    return Manager()


def _find_foreign_field_name(from_model, to_field_model):
    for key, value in from_model.__dict__.items():
        if isinstance(value, ForwardManyToOneDescriptor):
            if to_field_model == value.field.remote_field.model:
                return key
    assert False, f"Invalid  '{from_model.__name__}' model. " \
                  f"Can not find foregin field to {to_field_model.__name__}"


def get_model(model):
    return apps.get_model('v1_1', model) if isinstance(model, str) else model


class RecursionFindQuerySetMixin:

    def filter_recursive(self, **kwargs):
        fields = _find_foreign_field_name(self.model, self.model)
        table = f'{self.model._meta.app_label}_{self.model.__name__.lower()}'
        sql, params = self.filter(**kwargs).values('id').query.sql_with_params()
        params = tuple([f"'{p}'" if isinstance(p, str) else p for p in params])
        return self.filter(id__in=RawSQL(
            f"""
            WITH RECURSIVE r AS (
                SELECT id, parent_id, name, status
                FROM {table}
                WHERE id IN ({sql % params})
                UNION ALL
                SELECT {table}.id, {table}.parent_id, {table}.name, {table}.status
                FROM {table}
                     JOIN r
                          ON {' OR '.join([f'{table}.{field}_id = r.id' for field in fields])}
            )
            SELECT id FROM r""", ()
        ))
