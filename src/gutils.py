import networkx as nx
import random


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


def linearize(dag):
    """
    :param dag: A dag
    :return: list of node values in linearized order
    """
    if not nx.is_directed_acyclic_graph(dag):
        return AssertionError('Graph must be a Directed Acyclic Graph.')

    return list(nx.topological_sort(dag))


def extract_linearize(g):
    """
    Returns all nodes of the graph in a DFS tree
    :param g: graph
    :return: DFS tree
    """
    visited = set()
    not_visited = set(g.nodes())
    result = []
    while len(visited) != g.number_of_nodes():
        tree_set = set(nx.dfs_tree(g, random.sample(not_visited, 1)[0]))
        not_visited = not_visited.difference(tree_set)
        visited = visited.union(tree_set)

        # Add to the beginning of list.
        result = list(tree_set) + result

    return result
