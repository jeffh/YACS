class BaseConstraint(object):
    """Abstract class. The basic features provided to all constraints.
    """
    def extract_values(self, possible_solution):
        """Returns a tuple of the values that pertain to this constraint.

        It simply filters all values to by the variables this constraint uses.
        """
        r = [None] * len(self._vars)
        for var,val in possible_solution.iteritems():
            try:
                index = self._vars.index(var)
            except ValueError:
                continue
            r[index] = val
        return tuple(r)

class Constraint(BaseConstraint):
    """A simple constraint that takes any function. Less efficient in terms of limiting
    domain values because the solver doesn't fully understand the kinds of constraints
    the function imposes.
    """
    def __init__(self, func, variables, search_spaces):
        self._func, self._vars, self._search_spaces = func, variables, search_spaces
        
    def __call__(self, *args, **kwargs):
        if len(args) + len(kwargs) < len(self._vars):
            raise TypeError, "Constraint Function requires %r arguments" % len(self._vars)
        return self._func(*args, **kwargs)
    
    def __len__(self):
        "How constrainting this constraint is."
        return min(self._search_spaces)
        
    def __cmp__(self, other):
        return cmp(len(self), len(other))
    
