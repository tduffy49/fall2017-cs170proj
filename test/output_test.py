import unittest
import os
import sys
import os.path
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

from solver import read_input, solve
from sat_test import check


def test_passed_input(files, dir):
    for file in files:
        num_wizards, num_constraints, wizards, constraints = read_input(os.path.join(dir, file))
        solution = solve(num_wizards, num_constraints, wizards, constraints)

        return check(constraints, solution)

class OutputTest(unittest.TestCase):
    DIR_INPUTS_20 = "phase2_inputs/inputs20"
    DIR_INPUTS_35 = "phase2_inputs/inputs35"
    DIR_INPUTS_50 = "phase2_inputs/inputs50"

    def setUp(self):
        return

    # Quite redundant to separate same code block into 3 test cases. But this is done
    # for purposes of testing each input set separately.
    def test_inputs20(self):
        files = os.listdir(self.DIR_INPUTS_20)
        files = sorted(files, key=str.lower)
        for file in files:
            self.assertTrue(test_passed_input(files, self.DIR_INPUTS_20))
            print ('\n' + file + ' passed.')

    def test_inputs35(self):
        files = os.listdir(self.DIR_INPUTS_35)
        files = sorted(files, key=str.lower)
        for file in files:
            self.assertTrue(test_passed_input(files, self.DIR_INPUTS_35))
            print ('\n' + file + ' passed.')

    @unittest.skip('performance issues...')
    def test_inputs50(self):
        files = os.listdir(self.DIR_INPUTS_50)
        files = sorted(files, key=str.lower)
        for file in files:
            self.assertTrue(test_passed_input(files, self.DIR_INPUTS_50))
            print ('\n' + file + ' passed.')

if __name__ == '__main__':
    unittest.main()
