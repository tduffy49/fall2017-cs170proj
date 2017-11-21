import unittest
import sys
import os.path
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

import src.sat_reduce as sat
from satispy import Variable
from satispy.solver import Minisat

class TestSatMethods(unittest.TestCase):

    def test_touch_variable(self):
        mapping = {}
        sat.touch_variable('a', mapping)
        self.assertTrue(type(mapping['a']) == Variable)
        self.assertTrue(mapping['a'].name == 'a') # Variable has same name as its string mapping.


    def test_sat_basic(self):
        """Tests the case when Dumbledore is not between Harry and Hermione and Harry is not between
        Dumbledore and Hermione. So Dumbledore > Hermione > Harry."""
        cnf = sat.reduce([("Hermione", "Harry", "Dumbledore"), ("Hermione", "Dumbledore", "Harry")])
        solver = Minisat()
        solution = solver.solve(cnf)

        if not solution.success:
            self.fail("SAT failed to return a solution!")

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
