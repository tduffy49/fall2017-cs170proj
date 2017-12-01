import unittest
import sys
import os.path
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

import src.sat_reduce as sat
import src.gutils as dag
from satispy import Variable, Cnf
from satispy.solver import Minisat

def check(constraints, solution):
    """
    :param constraints: instance of WizardOrdering
    :param solution: supposed solution
    :return: True if `solution` is valid
    """
    for constraint in constraints:
        a, b, c = constraint
        ci = solution.index(c)
        bi = solution.index(b)
        ai = solution.index(a)
        v1 = (ci < ai and ci < bi)
        v2 = (ci > ai and ci > bi)
        if not (v1 or v2):
            return False

    return True

class TestPycosatReduction(unittest.TestCase):
    def test_reduce_pycosat(self):
        constraints = [("Hermione", "Harry", "Dumbledore"), ("Hermione", "Dumbledore", "Harry")]

        L = sat.LiteralTranslator(constraints)
        cnf = sat.reduce_pycosat([("Hermione", "Harry", "Dumbledore"), ("Hermione", "Dumbledore", "Harry")], L)
        solution = sat.run_pycosat(cnf)
        literals = sat.translate_pycosat(solution, L)
        G = dag.build_graph(literals)
        wizard_ordering = dag.linearize(G)

        self.assertTrue(check(constraints, wizard_ordering))

class TestSatispyReduction(unittest.TestCase):
    def setUp(self):
        self.skipTest('deprecated') # Skips whole test module.

    @unittest.skip('deprecated')
    def test_touch_variable(self):
        mapping = {}
        sat.touch_variable('a', mapping)
        self.assertTrue(type(mapping['a']) == Variable)
        self.assertTrue(mapping['a'].name == 'a') # Variable has same name as its string mapping.

    @unittest.skip('deprecated')
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

    @unittest.skip('deprecated')
    def test_sat_basic(self):
        """Tests the case when Dumbledore is not between Harry and Hermione and Harry is not between
        Dumbledore and Hermione. So Dumbledore > Hermione > Harry."""
        cnf = sat.reduce_satispy([("Hermione", "Harry", "Dumbledore"), ("Hermione", "Dumbledore", "Harry")])
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
