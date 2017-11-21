import unittest
import sys
import os.path
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

import src.sat_reduce as sat
from satispy import Variable, Cnf
from satispy.solver import Minisat

class TestSatMethods(unittest.TestCase):

    def test_touch_variable(self):
        mapping = {}
        sat.touch_variable('a', mapping)
        self.assertTrue(type(mapping['a']) == Variable)
        self.assertTrue(mapping['a'].name == 'a') # Variable has same name as its string mapping.

    def test_sat_lib(self):
        """Sanity check: (x1 v -x2), (-x2), (-x1), (x3 v x1 x x2)"""
        cnf = Cnf()
        x1 = Variable('x1'); x2 = Variable('x2'); x3 = Variable('x3')

        solver = Minisat()
        solution = solver.solve(cnf)

        if not solution.success:
            self.fail("Something seriously wrong with this library.")

        true_literals = [x3]
        false_literals = [x1, x2]

        for lit in true_literals:
            self.assertTrue(solution[lit])
        for lit in false_literals:
            self.assertFalse(solution[lit])

    def test_sat_basic(self):
        """Tests the case when Dumbledore is not between Harry and Hermione and Harry is not between
        Dumbledore and Hermione. So Dumbledore > Hermione > Harry."""
        cnf = sat.reduce([("Hermione", "Harry", "Dumbledore"), ("Hermione", "Dumbledore", "Harry")])
        solver = Minisat()
        solution = solver.solve(cnf)

        if not solution.success:
            self.fail("SAT failed to return a solution! This should not happen...")

        true_literals = ["Harry < Dumbledore", "Hermione < Dumbledore", "Harry < Dumbledore", "Harry < Hermione"]
        false_literals = ["Dumbledore < Harry", "Dumbledore < Hermione", "Dumbledore < Harry", "Hermione < Harry"]

        for lit in true_literals:
            self.assertTrue(solution[lit])
        for lit in false_literals:
            self.assertFalse(solution[lit])

    def test_reduction_sanity(self):
        return NotImplementedError

if __name__ == '__main__':
    unittest.main()
