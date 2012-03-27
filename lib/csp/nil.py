

class NilObject(object):
    """An object that represents no value.

    Math operations return the other value being operating upon with the exception of
    modulus, which return zero.

    Returns False for boolean operations. This means nil instances don't equal to each other.
    """

    def __repr__(self):
        return "<Nil>"

    @property
    def is_nil(self):
        return True

    def __nonzero__(self):
        return False

    def __eq__(self, other):
        return False

    def __lt__(self, other):
        return False

    def __gt__(self, other):
        return False

    def __add__(self, other):
        return other

    def __radd__(self, other):
        return other

    def __sub__(self, other):
        return other

    def __rsub__(self, other):
        return other

    def __mul__(self, other):
        return other

    def __rmul__(self, other):
        return other

    def __mul__(self, other):
        return other

    def __rmul__(self, other):
        return other

    def __mul__(self, other):
        return other

    def __rmul__(self, other):
        return other

    def __div__(self, other):
        return other

    def __rdiv__(self, other):
        return other

    def __mod__(self, other):
        return 0

    def __rmod__(self, other):
        return 0

    def __pow__(self, other):
        return other

    def __rpow__(self, other):
        return other

    def __neg__(self, other):
        return self


def is_nil(obj):
    "Returns True if the given object is a NilObject instance."
    return isinstance(obj, NilObject)
