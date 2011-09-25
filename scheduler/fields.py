from django.db import models

class SetOfIntegersField(models.CharField):
    description = "A sorted, comma separated set of integers. Unlike django's version, API usage is like a set of integers."

    # ensure django will call our subclass' methods
    __metaclass__ = models.SubfieldBase

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = kwargs.get('max_length', 255)
        self.delimiter = kwargs.pop('delimiter', ',')
        super(SetOfIntegersField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        if isinstance(value, SetOfIntegersField):
            return value

        if isinstance(value, set):
            return value

        if type(value) in (list, tuple):
            return set(value)
        
        if value == '':
            return set()
        values = set(int(x) for x in value.split(self.delimiter))

        return values

    def get_prep_value(self, value):
        return self.delimiter.join(str(x) for x in sorted(value))

    def get_prep_lookup(self, lookup_type, value):
        if lookup_type in ('exact', 'iexact'):
            result = self.get_prep_value(value)
            if lookup_type == 'iexact':
                result = result.lower()
            return result
        elif lookup_type == 'in':
            return [self.get_prep_value(v) for v in value]
        else:
            raise TypeError('Lookup type %r not supported.' % lookup_type)

try:
    from south.modelsinspector import add_introspection_rules
    rules = [
        (
            (SetOfIntegersField,),
            [],
            {
                'delimiter': ['delimiter', {'default': ','}],
                'max_length': ['max_length', {'default': 255}],
            }
        )
    ]
    add_introspection_rules(rules, ["^timetable\.scheduler\.fields"])
except ImportError:
    pass