import base64


def slugify(string):
    "The method used to convert an incoming string into a slug."
    slug = base64.b64encode(unicode(string), '-_')
    try:
        return slug[:slug.index('=')]
    except ValueError:
        return slug


def deserialize_numbers(numbers):
    if numbers == '[]':
        return []
    return tuple(sorted(int(x) for x in numbers.split(',') if x))


def serialize_numbers(numbers):
    return ','.join(str(s) for s in numbers)
