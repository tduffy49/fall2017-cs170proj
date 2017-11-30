import networkx as nx


def build_graph(lst):
    """
    For string "Name1<Name2", add and edge from name1 to name2.
    :param lst: list of edge strings, i.e. "Dumbledore<Harry"
    :return: a directed graph
    """
    G = nx.DiGraph()
    for elem in lst:
        name1, name2 = elem.split(" < ")
        # G.add_node is a set operation. Idempotent for same names.
        G.add_node(name1)
        G.add_node(name2)
        G.add_edge(name1, name2)
    return G

def build_dag(lst):
    G = nx.DiGraph()


def linearize(graph):
    """
    :param graph: A graph
    :return: list of node values in linearized order
    """
    if nx.is_directed_acyclic_graph(graph):
        return list(nx.topological_sort(graph))

    dag = nx.bfs_tree(graph)
    return list(nx.topological_sort(dag))

def extract_dag(g):
    """
    :param g: A directed graph, not necessarily acyclic
    :return: a DAG extracted
    """
    return NotImplementedError
