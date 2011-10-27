from constraints import Constraint, NilObject
from itertools import product
from abc import ABCMeta, abstractproperty, abstractmethod

__all__ = ['BruteForceSolver', 'BacktrackingSolver', 'DefaultSolver']

class SolverInterface(object):
    """Purely a reference class to understand the interface the Problem class expects."""
    __metaclass__ = ABCMeta

    @abstractproperty
    def solutions_seen(self):
        return 0

    @abstractmethod
    def set_conditions(self, variables, constraints):
        """Problem provided data.

        variables = {variable-name: list-of-domain-values}
        constraints = [(constraint_function, variable-names, default-variable-values)]
        """
        raise NotImplemented

    @abstractmethod
    def restore_point(self, starting_point=None):
        raise NotImplemented

    @abstractmethod
    def save_point(self):
        raise NotImplemented

    @abstractmethod
    def __iter__(self):
        raise NotImplemented

class BaseSolver(SolverInterface):
    def __init__(self):
        self._solutions_seen = 0
        self.restore_point()

    @property
    def solutions_seen(self):
        return self._solutions_seen

    def restore_point(self, start=None):
        self._start = start or 0
        return self

    def save_point(self):
        return self._solutions_seen

class BruteForceSolver(BaseSolver):
    """A naive solver that simply goes through every single possible combination
    and validates which solution is correct by testing it against all the constraints.

    """
    def _compute_search_spaces(self, used_variables):
        """Returns the size of each domain for a simple constraint size computation.
        This is used to pick the most constraining constraint first.
        """
        return tuple(len(domain) for name,domain in self._vars.iteritems())

    def satisfies_constraints(self, possible_solution):
        """Return True if the given solution is satisfied by all the constraints."""
        for c in self._constraints:
            values = c.extract_values(possible_solution)
            if values is None or not c(*values):
                return False
        return True

    def _compute_search_spaces(self, used_variables):
        """Returns the size of each domain for a simple constraint size computation.
        This is used to pick the most constraining constraint first.
        """
        return tuple(len(domain) for name,domain in self._vars.iteritems())

    def set_conditions(self, variables, constraints):
        """Problem provided data.

        variables = {variable-name: list-of-domain-values}
        constraints = [(constraint_function, variable-names, default-variable-values)]
        """
        self._vars, self._constraints = variables, []
        # build constraint objects
        for func, variables, values in constraints:
            c = Constraint(func, variables, values, self._compute_search_spaces(variables))
            self._constraints.append(c)
        # sort into most constraining first
        self._constraints.sort()
        #self._constraints.reverse() # most constrainting first

    def combinations(self):
        """Returns a generator of all possible combinations.
        """
        keys = self._vars.keys()
        for result in product(*self._vars.values()):
            possible_solution = {}
            for i,v in enumerate(result):
                possible_solution[keys[i]] = v
            yield possible_solution

    def __iter__(self):
        """Provide all the possible solutions.
        """
        self._solutions_seen = 0 # self._start
        iterator = self.combinations()
        for i in xrange(self._start):
            iterator.next()
        # for each combination
        for possible_solution in iterator:
            # "Solution:", possible_solution, '[valid]' if self.satisfies_constraints(possible_solution) else ''
            self._solutions_seen += 1
            # filter by all constraints
            if self.satisfies_constraints(possible_solution):
                yield possible_solution
        print "Visited", self.solutions_seen, "solutions"

class Solution(object):
    """Represents a JavaScript-like object.

    This is like a normal dictionary, except it can lookup keys on another 'base' dict
    if this dict doesn't have the given key.

    There is some aggressive caching for hashing and length computation, since they
    are used the most frequently.
    """
    def __init__(self, new=None, base=None):
        self.old, self.new = dict(base or {}), new or {}
        self._old_hash = None
        if isinstance(base, Solution):
            self._old_hash = hash(base)
        self._hash = None
        self._len = None

    def __repr__(self):
        r = {}
        r.update(self.old)
        r.update(self.new)
        return repr(r)

    def keys(self):
        "Returns all the keys this object can return proper values for."
        return tuple(set(self.new.keys()).union(self.old.keys()))

    def values(self):
        "Returns all values this object can return via keys."
        return tuple(set(self.new.values()).union(self.old.values()))

    def items(self):
        "Returns a generator of tuple pairs of (key, value)."
        for key in self.keys():
            yield (key, self[key])
    iteritems = items

    def get(self, key, default=None):
        return self.new.get(key, self.old.get(key, default))

    def __hash__(self):
        if self._hash is None:
            if self._old_hash:
                self._hash = hash(tuple(sorted(self.new.items()))) ^ self._old_hash
            else:
                self._hash = hash(tuple(sorted(self.items())))
        return self._hash

    def __iter__(self):
        return self.items()

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __len__(self):
        if self._len is None:
            self._len = len(set(self.new.keys()).union(self.old.keys()))
        return self._len

    _DoesNotExist = object()
    def __getitem__(self, key):
        result = self.new.get(key, self._DoesNotExist)
        if result is self._DoesNotExist:
            return self.old[key]
        return result

    def __setitem__(self, key, value):
        self.new[key] = value
        self._hash = None
        self._len = None

    def __contains__(self, key):
        return key in self.new or key in self.old

DefaultSolver = BruteForceSolver
