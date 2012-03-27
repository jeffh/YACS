from csp import Problem, BruteForceSolver, BacktrackingSolver
import unittest
from mock import Mock

# utility helpers


def assertEqualContents(actual, expected):
    for sol in actual:
        assert sol in expected, 'actual %r not in expected %r' % (sol, expected)
    for sol in expected:
        assert sol in actual, 'expected %r not in actual %r' % (sol, actual)


def assertIterEqual(iter1, iter2):
    iter1, iter2 = iter(iter1), iter(iter2)
    try:
        while 1:
            value1, value2 = next(iter1), next(iter2)
            assert value1 == value2, '%r != %r in iterators' % (value1, value2)
    except StopIteration:
        pass

    def hasNext(it):
        try:
            next(it)
            return True
        except StopIteration:
            return False

    if hasNext(iter1) or hasNext(iter2):
        return False
    return True


class BruteForceSolverTest(unittest.TestCase):
    def setUp(self):
        self.s = BruteForceSolver()
        self.s.set_conditions(
            variables={
                'x': range(3),
                'y': range(3),
            },
            constraints=[
                (lambda x, y: x != y, ['x', 'y'], ()),
            ]
        )
        self.expected = [
            {'x': 1, 'y': 0},
            {'x': 2, 'y': 0},
            {'x': 0, 'y': 1},
            {'x': 2, 'y': 1},
            {'x': 0, 'y': 2},
            {'x': 1, 'y': 2},
        ]

    def test_itersolution(self):
        assertIterEqual(self.expected, self.s)

    def test_solutions_seen_is_nonzero(self):
        list(self.s)
        self.assertNotEqual(self.s, 0)

    def test_solutions_at_points(self):
        list(self.s)
        assertIterEqual(self.expected, self.s.solutions_at_points.values())

    def test_reset(self):
        result1 = list(self.s)
        self.s.set_conditions(
            variables={
                'x': range(3),
                'y': range(3),
            },
            constraints=[
                (lambda x, y: x != y, ['x', 'y'], ()),
            ]
        )
        result2 = list(self.s)
        assertIterEqual(result1, result2)

    def test_save_and_restore(self):
        it = iter(self.s)
        values = next(it), next(it)
        ref = self.s.save_point()
        del it

        self.s.restore_point(ref)
        it = iter(self.s)
        value = next(it)
        self.assertFalse(value in values, 'Iterator was not restored properly.')


class BacktrackingSolverTest(unittest.TestCase):
    def setUp(self):
        self.s = BacktrackingSolver()
        self.s.set_conditions(
            variables={
                'x': range(3),
                'y': range(3),
            },
            constraints=[
                (lambda x, y: x != y, ['x', 'y'], ()),
            ]
        )
        self.expected = [
            {'x': 1, 'y': 0},
            {'x': 2, 'y': 0},
            {'x': 0, 'y': 1},
            {'x': 2, 'y': 1},
            {'x': 0, 'y': 2},
            {'x': 1, 'y': 2},
        ]

    def test_itersolution(self):
        assertIterEqual(self.expected, self.s)

    def test_solutions_seen_is_nonzero(self):
        list(self.s)
        self.assertNotEqual(self.s, 0)

    def test_solutions_at_points(self):
        list(self.s)
        assertIterEqual(self.expected, self.s.solutions_at_points.values())

    def test_reset(self):
        result1 = list(self.s)
        self.s.set_conditions(
            variables={
                'x': range(3),
                'y': range(3),
            },
            constraints=[
                (lambda x, y: x != y, ['x', 'y'], ()),
            ]
        )
        result2 = list(self.s)
        assertIterEqual(result1, result2)

    def test_save_and_restore(self):
        it = iter(self.s)
        values = next(it), next(it)
        ref = self.s.save_point()
        del it

        self.s.restore_point(ref)
        it = iter(self.s)
        value = next(it)
        self.assertFalse(value in values, 'Iterator was not restored properly.')


# integration tests
class PointConstraintIntegrationTest(unittest.TestCase):
    def setUp(self):
        self.p = Problem(BruteForceSolver())
        self.p.add_variable('x', range(3))
        self.p.add_variable('y', range(3))

    def result(self, *iter):
        return tuple(dict(x=x, y=y) for x, y in iter)

    def test_reset_problem(self):
        result1 = self.p.get_solutions()
        self.p.reset()
        self.p.add_variable('x', range(3))
        self.p.add_variable('y', range(3))
        result2 = self.p.get_solutions()
        self.assertEqual(result1, result2)

    def test_save_and_restore_iteration_position(self):
        it = self.p.iter_solutions()
        ref = self.p.save_point()
        second_answer = next(it)
        self.p.reset()
        self.p.add_variable('x', range(3))
        self.p.add_variable('y', range(3))
        self.p.restore_point(ref)
        answer = self.p.iter_solutions().next()
        #self.assertEqual(second_answer, answer)

    def test_with_no_constraints_should_have_all_permutations(self):
        #self.p.add_constraint(lambda x, y: x != y, ['x', 'y'])
        expected = self.result((0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2), (2, 0), (2, 1), (2, 2))
        assertEqualContents(self.p.get_solutions(), expected)

    def test_should_have_non_equal_permutations(self):
        expected = self.result((0, 1), (0, 2), (1, 0), (1, 2), (2, 0), (2, 1))
        self.p.add_constraint(lambda x, y: x != y, ['x', 'y'])
        assertEqualContents(self.p.get_solutions(), expected)

    def test_should_have_non_equal_permutations_or_sum_to_3(self):
        expected = self.result((0, 1), (0, 2), (1, 0), (2, 0))
        self.p.add_constraint(lambda x, y: x != y, ['x', 'y'])
        self.p.add_constraint(lambda x, y: x + y != 3, ['x', 'y'], [0, 0])
        assertEqualContents(self.p.get_solutions(), expected)

    def test_should_have_non_equal_permutations_while_x_is_lte_1(self):
        expected = self.result((0, 1), (0, 2), (1, 0), (1, 2))
        self.p.add_constraint(lambda x, y: x != y, ['x', 'y'])
        self.p.add_constraint(lambda x: x <= 1, ['x'], [0])
        assertEqualContents(self.p.get_solutions(), expected)


class PointConstaintIntegrationTestForBacktracker(unittest.TestCase):
    def setUp(self):
        self.p = Problem(BacktrackingSolver())
        self.p.add_variable('x', range(3))
        self.p.add_variable('y', range(3))

    def result(self, *iter):
        return tuple(dict(x=x, y=y) for x, y in iter)

    def test_reset_problem(self):
        result1 = self.p.get_solutions()
        self.p.reset()
        self.p.add_variable('x', range(3))
        self.p.add_variable('y', range(3))
        result2 = self.p.get_solutions()
        self.assertEqual(result1, result2)

    def test_save_and_restore_iteration_position(self):
        it = self.p.iter_solutions()
        next(it)
        ref = self.p.save_point()
        second_answer = next(it)
        self.p.reset()
        self.p.add_variable('x', range(3))
        self.p.add_variable('y', range(3))
        self.p.restore_point(ref)
        answer = next(self.p.iter_solutions())
        self.assertEqual(second_answer, answer)

    def test_with_no_constraints_should_have_all_permutations(self):
        #self.p.add_constraint(lambda x, y: x != y, ['x', 'y'])
        expected = self.result((0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2), (2, 0), (2, 1), (2, 2))
        assertEqualContents(self.p.get_solutions(), expected)

    def test_should_have_non_equal_permutations(self):
        expected = self.result((0, 1), (0, 2), (1, 0), (1, 2), (2, 0), (2, 1))
        self.p.add_constraint(lambda x, y: x != y, ['x', 'y'])
        assertEqualContents(self.p.get_solutions(), expected)

    def test_should_have_non_equal_permutations_or_sum_to_3(self):
        expected = self.result((0, 1), (0, 2), (1, 0), (2, 0))
        self.p.add_constraint(lambda x, y: x != y, ['x', 'y'])
        self.p.add_constraint(lambda x, y: x + y != 3, ['x', 'y'], [0, 0])
        assertEqualContents(self.p.get_solutions(), expected)

    def test_should_have_non_equal_permutations_while_x_is_lte_1(self):
        expected = self.result((0, 1), (0, 2), (1, 0), (1, 2))
        self.p.add_constraint(lambda x, y: x != y, ['x', 'y'])
        self.p.add_constraint(lambda x: x <= 1, ['x'], [0])
        assertEqualContents(self.p.get_solutions(), expected)


class SmallSolverrAccuracyIntegrationTest(unittest.TestCase):
    def setup_problem(self, p):
        p.add_variable('a', range(3))
        p.add_variable('b', range(3))
        p.add_variable('c', range(3))
        NE = lambda a, b: a != b
        p.add_constraint(NE, ['a', 'b'])
        p.add_constraint(NE, ['a', 'c'])
        p.add_constraint(NE, ['b', 'c'])
        return p

    def setUp(self):
        from itertools import product
        self.answer = tuple(
            dict(a=a, b=b, c=c) for a, b, c in product(range(3), range(3), range(3)) \
            if a not in (b, c) and b != c
        )

    def test_naive_solver(self):
        p = self.setup_problem(Problem(BruteForceSolver()))
        assertEqualContents(self.answer, p.get_solutions())
        self.assertEqual(p.solutions_seen, 27)

    def test_backtracking_solver(self):
        p = self.setup_problem(Problem(BacktrackingSolver()))
        assertEqualContents(self.answer, p.get_solutions())


class SolverAccuracyIntegrationTest(unittest.TestCase):
    def setUp(self):
        answerset = ((
            {'y': 0, 'x': 1, 'z': z},
            {'y': 0, 'x': 2, 'z': z},
            {'y': 0, 'x': 3, 'z': z},
            {'y': 0, 'x': 4, 'z': z},
            {'y': 0, 'x': 5, 'z': z},
            {'y': 0, 'x': 6, 'z': z},
            {'y': 0, 'x': 7, 'z': z},
            {'y': 0, 'x': 8, 'z': z},
            {'y': 0, 'x': 9, 'z': z},
            {'y': 1, 'x': 0, 'z': z},
            {'y': 1, 'x': 2, 'z': z},
            {'y': 1, 'x': 3, 'z': z},
            {'y': 1, 'x': 4, 'z': z},
            {'y': 1, 'x': 5, 'z': z},
            {'y': 1, 'x': 6, 'z': z},
            {'y': 1, 'x': 7, 'z': z},
            {'y': 1, 'x': 8, 'z': z},
            {'y': 2, 'x': 0, 'z': z},
            {'y': 2, 'x': 1, 'z': z},
            {'y': 2, 'x': 3, 'z': z},
            {'y': 2, 'x': 4, 'z': z},
            {'y': 2, 'x': 5, 'z': z},
            {'y': 2, 'x': 6, 'z': z},
            {'y': 2, 'x': 7, 'z': z},
            {'y': 3, 'x': 0, 'z': z},
            {'y': 3, 'x': 1, 'z': z},
            {'y': 3, 'x': 2, 'z': z},
            {'y': 3, 'x': 4, 'z': z},
            {'y': 3, 'x': 5, 'z': z},
            {'y': 3, 'x': 6, 'z': z},
            {'y': 4, 'x': 0, 'z': z},
            {'y': 4, 'x': 1, 'z': z},
            {'y': 4, 'x': 2, 'z': z},
            {'y': 4, 'x': 3, 'z': z},
            {'y': 4, 'x': 5, 'z': z},
            {'y': 5, 'x': 0, 'z': z},
            {'y': 5, 'x': 1, 'z': z},
            {'y': 5, 'x': 2, 'z': z},
            {'y': 5, 'x': 3, 'z': z},
            {'y': 5, 'x': 4, 'z': z},
            {'y': 6, 'x': 0, 'z': z},
            {'y': 6, 'x': 1, 'z': z},
            {'y': 6, 'x': 2, 'z': z},
            {'y': 6, 'x': 3, 'z': z},
            {'y': 7, 'x': 0, 'z': z},
            {'y': 7, 'x': 1, 'z': z},
            {'y': 7, 'x': 2, 'z': z},
            {'y': 8, 'x': 0, 'z': z},
            {'y': 8, 'x': 1, 'z': z},
            {'y': 9, 'x': 0, 'z': z},
        ) for z in range(3))
        self.answer = ()
        for a in answerset:
            self.answer += a

    def setup_problem(self, p):
        p.add_variable('x', range(10))
        p.add_variable('y', range(10))
        p.add_variable('z', range(3))
        p.add_constraint(lambda x, y: x != y, ['x', 'y'])
        p.add_constraint(lambda x, y: x + y < 10, ['x', 'y'], [0, 0])
        return p

    def test_naive_solver(self):
        p = self.setup_problem(Problem(BruteForceSolver()))
        assertEqualContents(self.answer, p.get_solutions())
        self.assertEqual(p.solutions_seen, 300)  # visited entire problem space

    def test_backtracking_solver(self):
        p = self.setup_problem(Problem(BacktrackingSolver()))
        assertEqualContents(self.answer, p.get_solutions())


if __name__ == '__main__':
    unittest.main()
