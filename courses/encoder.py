""" Handles the encoding of model objects for templates.
"""
from django.db.models import Model

from courses import models

def get_fields(model):
    return model._meta.fields

def get_fk_fields(model):
    return [f for f in get_fields(model) if f.rel]

def get_normal_fields(model):
    return [f for f in get_fields(model) if not f.rel]

def get_field_names(model):
    return [f.name for f in get_fields(model)]

def get_normal_field_names(model):
    return [f.name for f in get_normal_fields(model)]

def get_fk_field_names(model):
    return [f.name for f in get_fk_fields(model)]

def generate_select_related(model, max_depth=1):
    if max_depth < 1:
        return {}
    select_related = {}
    for field in get_fields(model):
        if field.rel: # related (foreign key) field
            parent_model = field.related.parent_model
            select_related[field.name] = generate_select_related(parent_model, max_depth-1)
        else:
            select_related[field.name] = {}
    return select_related

def has_deferred_fields(queryset):
    fields, is_excluded = queryset.query.deferred_loading
    return not (is_excluded and not fields)

def requires_manually_related_scan(queryset):
    return queryset.query.select_related == True

def get_select_related_fields(queryset):
    model = queryset.model
    if has_deferred_fields(queryset):
        print "WARNING: Encoder does not support deferred fields."
    if requires_manually_related_scan(queryset):
        depth = queryset.query.max_depth
        # we have to find them all ourselves
        return generate_select_related(model, depth)
    return queryset.query.select_related

def get_prefetch_cache(model):
    return getattr(model, '_prefetched_objects_cache', {})


class Encoder(object):
    def encode_normal_fields(self, model):
        obj = {}
        for field_name in get_normal_field_names(model):
            obj[field_name] = getattr(model, field_name)
        return obj

    def encode_fk_fields(self, model):
        obj = {}
        for field in get_fk_fields(model):
            obj[field.name + '_id'] = getattr(model, field.column)
        return obj

    def encode_select_related(self, model, select_related=None):
        obj = {}
        for field_name, subfields in (select_related or {}).items():
            value = getattr(model, field_name)
            # if a model instance
            if hasattr(value, '_meta'):
                obj[field_name] = self.encode_model(value, subfields)
            else: # just a normal field
                obj[field_name] = value
        return obj

    def encode_prefetch_cache(self, model):
        obj = {}
        cache = get_prefetch_cache(model)
        for field_name, instances in cache.items():
            obj[field_name] = [self.encode_model(m) for m in instances]
        return obj

    def encode_model(self, model, select_related=None):
        obj = {}
        obj.update(self.encode_normal_fields(model))
        obj.update(self.encode_fk_fields(model))
        obj.update(self.encode_select_related(model, select_related))
        obj.update(self.encode_prefetch_cache(model))
        return obj

    def encode_queryset(self, queryset, read_select_related=True):
        select_related = ()
        if read_select_related:
            select_related = get_select_related_fields(queryset)
        return [self.encode_model(m, select_related) for m in queryset]

    def encode(self, value):
        if hasattr(value, 'query'): # queryset
            return self.encode_queryset(value)
        elif hasattr(value, '_meta'): # model
            return self.encode_model(value)
        elif isinstance(value, list) or isinstance(value, tuple):
            if len(value) and hasattr(value[0], '_meta'):
                return list(map(self.encode_model, value))
        elif isinstance(value, dict):
            for key in value.keys():
                value[key] = self.encode(value[key])
        return value


default_encoder = Encoder()

