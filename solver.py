import argparse
import networkx as nx

"""
======================================================================
  Complete the following function.
======================================================================
"""
def build_dag(lst):
    """
    For string "<name1><<name2>", add and edge from name1 to name2.
    :param lst: list of edge strings, i.e. "Dumbledore<Harry"
    :return: a DAG
    """
    G = nx.DiGraph()
    for elem in lst:
        name1, name2 = elem.split("<")
        G.add_node(name1) # add_node is set operation. Idempotent for same names.
        G.add_node(name2)
        G.add_edge(name1, name2)
    return G

def find_source(dag):
    for node in dag.nodes():
        if dag.in_degree(node) == 0:
            return node

def linearize(dag):
    """
    :param dag: DAG
    :return: linearized DAG
    """
    source = find_source(dag)
    assert(source)

    postorder = list(nx.dfs_postorder_nodes(dag, source))
    postorder.reverse()
    return postorder

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
