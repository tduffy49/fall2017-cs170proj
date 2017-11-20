import argparse
from satispy import Variable, Cnf
from satispy.solver import Minisat
"""
======================================================================
  Complete the following function.
======================================================================
"""

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
        
        exp &= (x_1 | x_2) & (x_3 | x_4) & (~x_1 | ~x_4) & (~x_2 | ~x_3)

    solver = Minisat()
    solution = solver.solve(exp)

    return []

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
