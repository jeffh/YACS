from json import dumps, JSONEncoder

class ObjectJSONEncoder(JSONEncoder):
    def default(self, o):
        if callable(getattr(o, 'toJSON', None)):
            return o.toJSON()
        return super(ObjectJSONEncoder, self).default(o)

class ExtendedAttributeError(AttributeError):
    def __init__(self, msg, obj, full_attr, error_attr):
        super(ExtendedAttributeError, self).__init__(msg % {
            'obj': obj,
            'full_attr': full_attr, # the full path we were trying to access
            'error_attr': error_attr, # the attr access that caused the error
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
        value = getattr(value, name, _NONE)
        if value == _NONE:
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
