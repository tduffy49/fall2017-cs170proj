import argparse
import src.dag_utils as dg
import src.sat_reduce as sr
import pycosat
import itertools

from satispy import Variable, Cnf
from satispy.solver import Minisat

"""
======================================================================
  Complete the following function.
======================================================================
"""


def remove_bad_constraints(constraints):
    good_constraints = list()
    for c in constraints:
        # First 2 elements in constraint list are the same
        if c[0] == c[1]:
            continue
        reversed_constraint = [c[1], c[0], c[2]]
        # First 2 elements in constraint are reversed order of constraint already
        # Accounted for or duplicate constraint
        if reversed_constraint in good_constraints or c in good_constraints:
            continue
        good_constraints.append(c)
    return good_constraints


def num_constraints_satisfied(num_wizards, constraints, ordering):
    if (len(ordering) != num_wizards):
        # print("Input file has unique {} wizards, but output file has {}".format(num_wizards, len(ordering)))
        return 0
    
    # Counts how many constraints are satisfied.
    constraints_satisfied = 0
    output_ordering_map = {k: v for v, k in enumerate(ordering)}
    for constraint in constraints:
        c = constraint # Creating an alias for easy reference
        m = output_ordering_map # Creating an alias for easy reference
        
        wiz_a = m[c[0]]
        wiz_b = m[c[1]]
        wiz_mid = m[c[2]]
        
        if (wiz_a < wiz_mid < wiz_b) or (wiz_b < wiz_mid < wiz_a):
            pass
        else:
            constraints_satisfied += 1

    return constraints_satisfied


def original_solver(constraints):
    variables = {}

    def get_variable(name):
        if name in variables:
            var = variables[name]
        else:
            var = Variable(name)
            variables[name] = var
        return var

    exp = Cnf()
    for constraint in constraints:
        a, b, c = constraint
        x_1 = get_variable('%s<%s' % (a, c))
        x_2 = get_variable('%s<%s' % (c, a))
        x_3 = get_variable('%s<%s' % (b, c))
        x_4 = get_variable('%s<%s' % (c, b))
        exp &= (x_1 | x_2) & (x_3 | x_4) & (-x_1 | -x_4) & (-x_2 | -x_3)

    solver = Minisat()
    solution = solver.solve(exp)

    valid = []
    if solution.success:
        for var in variables:
            key = variables[var]
            if solution[key]:
                valid.append(var)
    else:
        print('No solution')
        return []

    return valid


def pycosat_solve(constraints, limit):
    cnf = list()
    clauses = dict()
    reverse_clauses = dict()
    unique_constraints = remove_bad_constraints(constraints)
    
    i = 1 #pycosat variables must be non-zero
    for constraint in unique_constraints:
        a, b, c = constraint
        x_1 = '{0}<{1}'.format(a, c)
        x_2 = '{0}<{1}'.format(c, a)
        x_3 = '{0}<{1}'.format(b, c)
        x_4 = '{0}<{1}'.format(c, b)
        if x_1 not in clauses:
            clauses[x_1] = i
            reverse_clauses[i] = x_1
            i += 1
        if x_2 not in clauses:
            clauses[x_2] = i
            reverse_clauses[i] = x_2
            i += 1
        if x_3 not in clauses:
            clauses[x_3] = i
            reverse_clauses[i] = x_3
            i += 1
        if x_4 not in clauses:
            clauses[x_4] = i
            reverse_clauses[i] = x_4
            i += 1
        cnf.append([clauses[x_1], clauses[x_2]])
        cnf.append([clauses[x_3], clauses[x_4]])
        cnf.append([-clauses[x_1], -clauses[x_4]])
        cnf.append([-clauses[x_2], -clauses[x_3]])
    
    solutions = []
    solution_list = itertools.islice(pycosat.itersolve(cnf), limit)

    for sol in solution_list:
        c = list()
        for var in sol:
            if var >  0: #true variables are positive, false are negative
                c.append(reverse_clauses[var])
            solutions.append(c)
    
    return solutions


def solve(num_wizards, num_constraints, wizards, constraints):
    """
    Write your algorithm here.
    Input:
        num_wizards: Number of wizards
        num_constraints: Number of constraints
        wizards: An array of wizard names, in no particular order
        constraints: A 2D-array of constraints, 
                     where constraints[0] may take the form ['A', 'B', 'C']i

    Output:
        An array of wizard names in the ordering your algorithm returns
    """
    L = sr.LiteralTranslator()
    cnf = sr.reduce_pycosat(constraints, L)
    solution = sr.solve_pycosat(cnf)

    return sr.translate_pycosat(solution, L)


"""
======================================================================
   No need to change any code below this line
======================================================================
"""

def read_input(filename):
    with open(filename) as f:
        num_wizards = int(f.readline())
        num_constraints = int(f.readline())
        constraints = []
        wizards = set()
        for _ in range(num_constraints):
            c = f.readline().split()
            constraints.append(c)
            for w in c:
                wizards.add(w)
                
    wizards = list(wizards)
    return num_wizards, num_constraints, wizards, constraints


def write_output(filename, solution):
    with open(filename, "w") as f:
        for wizard in solution:
            f.write("{0} ".format(wizard))


if __name__=="__main__":
    parser = argparse.ArgumentParser(description = "Constraint Solver.")
    parser.add_argument("input_file", type=str, help = "___.in")
    parser.add_argument("output_file", type=str, help = "___.out")
    args = parser.parse_args()

    num_wizards, num_constraints, wizards, constraints = read_input(args.input_file)
    solution = solve(num_wizards, num_constraints, wizards, constraints)
    write_output(args.output_file, solution)
