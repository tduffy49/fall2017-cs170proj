import unittest
import sys
import os.path
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

import src.dag_utils as dg

class TestDagMethods(unittest.TestCase):

    def test_linearize_basic(self):
        G = dg.build_dag(["Hermione < Dumbledore", "Harry < Dumbledore", "Hermione < Snape",
                          "Hermione < Harry", "Snape < Dumbledore"])
        result = dg.linearize(G)
        self.assertEqual(result, ["Hermione", "Harry", "Snape", "Dumbledore"])

    def test_linearize_multiple_source(self):
        G = dg.build_dag(["Hermione < Dumbledore", "Snape < Dumbledore", "Harry < Snape"])
        result = dg.linearize(G)
        valid = (result == ["Hermione", "Harry", "Snape", "Dumbledore"]) | \
                (result == ["Harry", "Snape", "Hermione", "Dumbledore"]) | \
                (result == ["Harry", "Hermione", "Snape", "Dumbledore"])
        self.assertTrue(valid)

    def test_linearize_multiple_sink(self):
        G = dg.build_dag(["Harry < Dumbledore", "Harry < Snape", "Hermione < Harry"])
        result = dg.linearize(G)
        valid = (result == ["Hermione", "Harry", "Snape", "Dumbledore"]) | \
                (result == ["Hermione", "Harry", "Dumbledore", "Snape"])
        self.assertTrue(valid)


if __name__ == '__main__':
    unittest.main()
