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


def extract_dfs_linearize(g):
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


def extract_linearize(g):
    """
    Extract a DAG from g and returns topological ordering
    :param g: DiGraph
    :return: list of nodes
    """
    nodes = list(g.nodes())
    random.shuffle(nodes)
    set1, set2 = set(), set()
    for edge in g.edges():
        src, dest = edge
        src_i, dest_i = nodes.index(src), nodes.index(dest)
        if src_i > dest_i:
            set1.add(edge)
        else:
            set2.add(edge)

    # Choose set with larger edges.
    G = nx.DiGraph()
    G.add_nodes_from(g.nodes())
    if len(set1) > len(set2):
        G.add_edges_from(set1)
    else:
        G.add_edges_from(set2)

    assert (nx.is_directed_acyclic_graph(G))
    return linearize(G)