from constraints import Constraint
from itertools import product

__all__ = ['SimpleSolver']

class SimpleSolver(object):
    """A naive solver that simply goes through every single possible combination
    and validates which solution is correct by testing it against all the constraints.
    
    """
    def __init__(self):
        pass
        
    def _compute_search_spaces(self, used_variables):
        """Returns the size of each domain for a simple constraint size computation.
        This is used to pick the most constraining constraint first.
        """
        return tuple(len(domain) for name,domain in self._vars.iteritems())
    
    def set_conditions(self, variables, constraints):
        """Problem provided data.
        
        variables = {variable-name: list-of-domain-values}
        constraints = [(constraint_function, variable-names)]
        """
        self._vars, self._constraints = variables, []
        # build constraint objects
        for func, variables in constraints:
            c = Constraint(func, variables, self._compute_search_spaces(variables))
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
    
    def satisfies_constraints(self, possible_solution):
        """Return True if the given solution is satisfied by all the constraints."""
        for c in self._constraints:
            values = c.extract_values(possible_solution)
            if values is None or not c(*values):
                return False
        return True
        
    def __iter__(self):
        """Provide all the possible solutions.
        """
        # for each combination
        for possible_solution in self.combinations():
            # filter by all constraints
            if self.satisfies_constraints(possible_solution):
                yield possible_solution
