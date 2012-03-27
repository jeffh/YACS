import collections

from config import logger


def safeInt(n, warn_only=False):
    """Throws an exception if the number starts with a 0 (may be significant).

    If the value cannot be converted to an int, it is returned as is.
    """
    if str(n).startswith('0'):
        if not warn_only:
            raise TypeError("Unsafe Int: " + str(n))
        print "Unsafe Int: %s" % n
        return int(n)
    try:
        return int(n)
    except ValueError:
        return n


# from SO: http://stackoverflow.com/questions/2703599/what-would-be-a-frozen-dict
class FrozenDict(collections.Mapping):
    """Defines an immutable dict type."""

    FROZEN_TYPES = {
        set: frozenset,
        list: tuple,
    }

    def __init__(self, *args, **kwargs):
        self._hash = None
        self._d = {}
        for key, vals in dict(*args, **kwargs).items():
            self._d[self._freeze(key)] = self._freeze(vals)

    def _freeze(self, value):
        return self.FROZEN_TYPES.get(type(value), lambda x: x)(value)

    def __iter__(self):
        return iter(self._d)

    def __len__(self):
        return len(self._d)

    def __getitem__(self, key):
        return self._d[key]

    def __setitem__(self, key, value):
        raise TypeError("FrozenDict is immutable.")

    def __repr__(self):
        return "FrozenDict(%r)" % self._d

    def __hash__(self):
        if self._hash is None:
            self._hash = 0
            for key, value in self.iteritems():
                self._hash ^= hash(key)
                self._hash ^= hash(value)
        return self._hash

FrozenDict.FROZEN_TYPES[dict] = FrozenDict
