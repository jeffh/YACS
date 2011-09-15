from csp.problem import Problem
import unittest

class PointConstraintProblem(unittest.TestCase):
    def setUp(self):
        self.p = Problem()
        self.p.add_variable('x', range(3))
        self.p.add_variable('y', range(3))
        
    def result(self, *iter):
        return tuple(dict(x=x, y=y) for x,y in iter)
    
    def cmp(self, actual, expected):
        for sol in actual:
            assert sol in expected, 'actual %r not in expected %r' % (sol, expected)
        for sol in expected:
            assert sol in actual, 'expected %r not in actual %r' % (sol, actual)
        
    def test_with_no_constraints_should_have_all_permutations(self):
        #self.p.add_constraint(lambda x,y: x != y, ['x', 'y'])
        expected = self.result((0, 0), (0,1), (0, 2), (1,0), (1, 1), (1, 2), (2,0), (2, 1), (2,2))
        self.cmp(self.p.get_solutions(), expected)
        
    def test_should_have_non_equal_permutations(self):
        expected = self.result((0,1), (0, 2), (1,0), (1, 2), (2,0), (2, 1))
        self.p.add_constraint(lambda x,y: x != y, ['x', 'y'])
        self.cmp(self.p.get_solutions(), expected)
        
    def test_should_have_non_equal_permutations_or_sum_to_3(self):
        expected = self.result((0,1), (0, 2), (1,0), (2,0))
        self.p.add_constraint(lambda x,y: x != y, ['x', 'y'])
        self.p.add_constraint(lambda x,y: x+y != 3, ['x', 'y'])
        self.cmp(self.p.get_solutions(), expected)
        
    def test_should_have_non_equal_permutations_while_x_is_lte_1(self):    
        expected = self.result((0,1), (0, 2), (1,0), (1, 2))
        self.p.add_constraint(lambda x,y: x != y, ['x', 'y'])
        self.p.add_constraint(lambda x: x <= 1, ['x'])
        self.cmp(self.p.get_solutions(), expected)

if __name__ == '__main__':
    unittest.main()
