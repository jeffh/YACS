from json import dumps, JSONEncoder
import datetime

DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']  # , 'Saturday', 'Sunday']


def sorted_daysofweek(dow, days=DAYS):
    "Sorts list of days of the week to what we're expected."
    dow = set(dow)
    return [d for d in days if d in dow]


class ObjectJSONEncoder(JSONEncoder):
    def default(self, o):
        if callable(getattr(o, 'toJSON', None)):
            return o.toJSON()
        if isinstance(o, datetime.datetime) or isinstance(o, datetime.date) or isinstance(o, datetime.time):
            return o.isoformat()
        return super(ObjectJSONEncoder, self).default(o)


class ExtendedAttributeError(AttributeError):
    def __init__(self, msg, obj, full_attr, error_attr):
        super(ExtendedAttributeError, self).__init__(msg % {
            'obj': obj,
            'full_attr': full_attr,  # the full path we were trying to access
            'error_attr': error_attr,  # the attr access that caused the error
        })
        self.obj = obj
        self.full_attr = full_attr
        self.error_attr = error_attr


_NONE = object()


def extended_getattr(obj, attrpath, default=_NONE):
    """Like getattr, but allows the attrname to be a dot-path notation::

      extended_getattr(obj, 'a.b') == obj.a.b
    """
    path = str(attrpath).split('.')
    value = obj
    for name in path:
        value = getattr(value, name, default)
        if value is _NONE:
            raise ExtendedAttributeError("%(obj)r does not have attribute %(error_attr)r when trying to walk %(full_attr)r", value, attrpath, name)
    return value


def dict_by_attr(collection, attrname, value_attrname=None):
    """Creates a dictionary of a collection using a specific attribute name of each item as the key.
    Uses a list as the value to avoid overwriting objects with duplicate key values.

    Alternatively, attrname can be a function that returns the key to store the object into.
    """
    mapping = {}
    for item in collection:
        if callable(attrname):
            key = attrname(item)
        else:
            key = extended_getattr(item, attrname)
        if value_attrname:
            item = extended_getattr(item, value_attrname)
        mapping[key] = mapping.get(key, []) + [item]
    return mapping


def int_list(str_of_integers):
    if not str_of_integers:
        return []
    ints = set()
    for num in str_of_integers:
        try:
            ints.add(int(num))
        except (ValueError, TypeError):
            pass
    return list(ints)


def options(amount=None):
    """Provides values for options which can be ORed together.

    If no amount is provided, returns a generator of ever growing numerical values starting from 1.
    If amount is provided, returns a amount-sized list of numerical values.
    """
    def generator():
        exp = 0
        cache = None
        while 1:
            if cache:
                cache = cache * 2
            else:
                cache = 2 ** exp
            yield cache
            exp += 1
    if amount is None:
        return generator()
    return [v for _, v in zip(range(amount), generator())]


def capitalized(string):
    "Capitalizes the first character in the given string."
    return string[0:1].upper() + string[1:].lower()


class Synchronizer(object):
    """Handles the creation of models.
    Can delete models that were not 'created'.

    When inverse_trim = False, the instances are deleted using an exclude()
    otherwise, the instances are deleted using a filter() - which requires an
    extra query.

    On systems when the database query execution time is short, using
    the inverse_trim may be faster.
    """
    def __init__(self, model, inverse_trim=True):
        self.model = model
        self.inverse_trim = inverse_trim
        self.ids_used = set()

    def exclude_id(self, id):
        self.ids_used.add(id)

    def get_or_create(self, **kwargs):
        model, created = self.model.objects.get_or_create(**kwargs)
        self.exclude_id(model.id)
        return model, created

    def create(self, **kwargs):
        model = self.model.objects.create(**kwargs)
        self.exclude_id(model.id)
        return model

    def trim(self, **filter):
        "Removes models that were not get_or_create'd. Can optionally be filtered."
        qs = self.model.objects.exclude(id__in=self.ids_used)
        if self.inverse_trim:
            ids = set(self.model.objects.filter(**filter).values_list('id', flat=True))
            ids_to_delete = ids.difference(self.ids_used)
            qs = self.model.objects.filter(id__in=ids_to_delete)
            if not ids_to_delete:
                return
        qs.filter(**filter).delete()
