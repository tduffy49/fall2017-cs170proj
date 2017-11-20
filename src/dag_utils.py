import networkx as nx

def build_dag(lst):
    """
    For string "Name1<Name2", add and edge from name1 to name2.
    :param lst: list of edge strings, i.e. "Dumbledore<Harry"
    :return: a DAG
    """
    G = nx.DiGraph()
    for elem in lst:
        name1, name2 = elem.split(" < ")
        G.add_node(name1) # add_node is set operation. Idempotent for same names.
        G.add_node(name2)
        G.add_edge(name1, name2)
    return G

def linearize(dag):
    """
    :param dag: DAG
    :return: list of node values in linearized order
    """
    return list(nx.topological_sort(dag))