from nil import NilObject

class BaseConstraint(object):
    """Abstract class. The basic features provided to all constraints.
    """
    def __init__(self, variables, values):
        self._vars, self._values = variables, values
        self._vardefaults = dict(zip(self._vars, self._values))
        self._template = [None] * len(self._vars)

    def extract_values(self, possible_solution, use_defaults=False):
        """Returns a tuple of the values that pertain to this constraint.

        It simply filters all values to by the variables this constraint uses.
        """
        defaults = self._vardefaults if use_defaults else {}
        values = list(self._template)
        for i, var in enumerate(self._vars):
            values[i] = possible_solution.get(var, defaults.get(var, NilObject()))
        return values

    def __len__(self):
        return 99999

    def __cmp__(self, other):
        return cmp(len(self), len(other))

class Constraint(BaseConstraint):
    """A simple constraint that takes any function. Less efficient in terms of limiting
    domain values because the solver doesn't fully understand the kinds of constraints
    the function imposes.
    """
    def __init__(self, func, variables, values, search_spaces):
        super(Constraint, self).__init__(variables, values)
        self._func, self._search_spaces = func, search_spaces

    def __call__(self, *args, **kwargs):
        if len(args) + len(kwargs) < len(self._vars):
            raise TypeError, "Constraint Function requires %r arguments" % len(self._vars)
        return self._func(*args, **kwargs)

    def __len__(self):
        "How constrainting this constraint is."
        return min(self._search_spaces)
