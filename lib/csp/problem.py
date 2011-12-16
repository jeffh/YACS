from solvers import DefaultSolver

class Problem(object):
    """Represents a problem space that needs solutions.

    Optionally, solver_instance can be set to provide a more customized solver.
    """
    def __init__(self, solver_instance=None):
        if solver_instance is None:
            solver_instance = DefaultSolver()
        self._solver_instance = solver_instance
        self.reset()

    @property
    def solutions_seen(self):
        """Returns the total number of complete possible solutions seen by the solver.
        Will be zero if no solution finding has been done yet.
        """
        return self._solver_instance.solutions_seen

    def reset(self):
        self._variables = {} # variable: list-domain-of-variable
        self._constraints = [] # (constraint_function, variables)
        self._restore_point = None

    def add_variable(self, variable, domain):
        """Adds a variable that needs a value to be determined in the given problem.

        The variable should be hashable and comparable.
        The domain is the list of possible values the given variable can be.
        """
        self._variables[variable] = list(domain)

    def add_constraint(self, func, variables, default_values=None):
        """Adds a constraint that applies to one or more variables.

        The function must return true or false to indicate which combinations
        of variable values are valid.
        """
        self._constraints.append((func, variables, default_values or ()))

    def setup(self):
        self._solver_instance.set_conditions(dict(self._variables), list(self._constraints))
        self._solver_instance.restore_point(self._restore_point)

    def iter_solutions(self):
        "Returns a generator of solutions to the given constraints problem."
        self.setup()
        return iter(self._solver_instance)

    def get_solutions(self):
        "Returns a tuple of all the solutions to the given constraints problem."
        return tuple(self.iter_solutions())

    def restore_point(self, start):
        self._restore_point = start
        return self

    def save_point(self):
        return self._solver_instance.save_point()

    def known_solutions(self):
        return self._solver_instance.solutions_at_points

    def __repr__(self):
        return "<Problem(variables=%(v)r, constraints=%(c)r), solver=%(s)r>" % {
            'v': self._variables,
            'c': self._constraints,
            's': self._solver_instance.__class__,
        }
