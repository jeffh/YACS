import collections
from config import logger

def safeInt(n):
    """Throws an exception if the number starts with a 0 (may be significant).
    
    If the value cannot be converted to an int, it is returned as is.
    """
    if str(n).startswith('0'):
        raise TypeError, "Unsafe Int: "+str(n)
    try:
        return int(n)
    except ValueError:
        return n

# from SO: http://stackoverflow.com/questions/2703599/what-would-be-a-frozen-dict
class FrozenDict(collections.Mapping):
    """Defines an immutable dict type."""

    def __init__(self, *args, **kwargs):
        self._d = dict(*args, **kwargs)
        self._hash = None

    def __iter__(self):
        return iter(self._d)

    def __len__(self):
        return len(self._d)

    def __getitem__(self, key):
        return self._d[key]
        
    def __setitem__(self, key, value):
        raise TypeError, "FrozenDict is immutable."

    def __hash__(self):
        # It would have been simpler and maybe more obvious to 
        # use hash(tuple(sorted(self._d.iteritems()))) from this discussion
        # so far, but this solution is O(n). I don't know what kind of 
        # n we are going to run into, but sometimes it's hard to resist the 
        # urge to optimize when it will gain improved algorithmic performance.
        if self._hash is None:
            self._hash = 0
            for key, value in self.iteritems():
                self._hash ^= hash(key)
                self._hash ^= hash(value)
        return self._hash