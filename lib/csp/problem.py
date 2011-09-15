from solvers import SimpleSolver

class Problem(object):
    """Represents a problem space that needs solutions.
    
    Optionally, solver_instance can be set to provide a more customized solver.
    """
    def __init__(self, solver_instance=None):
        if solver_instance is None:
            solver_instance = SimpleSolver()
        self._solver_instance = solver_instance
        self.reset()
    
    def reset(self):    
        self._variables = {} # variable: list-domain-of-variable
        self._constraints = [] # (constraint_function, variables)
    
    def add_variable(self, variable, domain):
        """Adds a variable that needs a value to be determined in the given problem.
        
        The variable should be hashable and comparable.
        The domain is the list of possible values the given variable can be.
        """
        self._variables[variable] = list(domain)
    
    def add_constraint(self, func, variables):
        """Adds a constraint that applies to one or more variables.
        
        The function must return true or false to indicate which combinations
        of variable values are valid.
        """
        self._constraints.append((func, variables))
        
    def iter_solutions(self):
        self._solver_instance.set_conditions(dict(self._variables), list(self._constraints))
        return iter(self._solver_instance)
    
    def get_solutions(self):
        return tuple(self.iter_solutions())
    
    def get_all_possible_solutions(self):
        self._solver_instance.set_conditions(dict(self._variables), list(self._constraints))
        return self._solver_instance.combinations()
        
    def __repr__(self):
        return "<Problem(variables=%(v)r, constraints=%(c)r), solver=%(s)r>" % {
            'v': self._variables,
            'c': self._constraints,
            's': self._solver_instance.__class__,
        }