import unittest
import os
import sys
import os.path
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

from solver import read_input, solve
from sat_test import check

class OutputTest(unittest.TestCase):
    DIR_INPUTS_20 = "phase2_inputs/inputs20"

    def setUp(self):
        return

    def test_inputs20(self):
        files = os.listdir(self.DIR_INPUTS_20)
        files = sorted(files, key=str.lower)
        for file in files:
            num_wizards, num_constraints, wizards, constraints = read_input(os.path.join(self.DIR_INPUTS_20, file))
            solution = solve(num_wizards, num_constraints, wizards, constraints)
            self.assertTrue(check(constraints, solution))
            print ('\n' + file + ' passed.')

if __name__ == '__main__':
    unittest.main()
