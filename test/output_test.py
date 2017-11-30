import unittest
import os
import sys
import os.path
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

from solver import read_input, write_output, solve
from sat_test import check

# Determines whether tests should also write output of solution to file.
SHOULD_WRITE_OUTPUT = True


def test_passed_input(file, dir):
    num_wizards, num_constraints, wizards, constraints = read_input(os.path.join(dir, file))
    solution = solve(num_wizards, num_constraints, wizards, constraints)

    if SHOULD_WRITE_OUTPUT and check(constraints, solution):
        out_dir = dir.replace('input', 'output')
        out_file = file.replace('.in', '.out')
        write_output(os.path.join(out_dir, out_file), solution)

    return check(constraints, solution)


class OutputTest(unittest.TestCase):
    DIR_INPUTS_20 = "phase2_inputs/inputs20"
    DIR_INPUTS_35 = "phase2_inputs/inputs35"
    DIR_INPUTS_50 = "phase2_inputs/inputs50"

    DIR_TESTS = [DIR_INPUTS_20, DIR_INPUTS_35, DIR_INPUTS_50]
    DIR_STAFF = "staff_inputs"

    def test_inputs(self):
        for dir in self.DIR_TESTS:
            files = os.listdir(dir)
            files = sorted(files, key=str.lower)
            for file in files:
                self.assertTrue(test_passed_input(file, dir))
                print (file + ' passed.')

    def test_staff_inputs(self):
        files = os.listdir(self.DIR_STAFF)
        files = sorted(files, key=str.lower)
        for file in files:
            print ('Testing: ' + file)
            self.assertTrue(test_passed_input(file, self.DIR_STAFF))
            print (file + ' passed.')

if __name__ == '__main__':
    unittest.main()
