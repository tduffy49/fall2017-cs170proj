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


def extract_max_dag(g):
    """
    Extract a maximum edge DAG from `g` with approx. factor of 2
    :param g: a DiGraph
    :return: DAG
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

    return G


def add_random_edges(dag, num):
    """
    :param dag: DAG
    :param num: number of edges to add
    :return: None
    """
    num_added = 0
    ordering = linearize(dag)
    while num_added < num:
        i1 = random.randint(0, len(ordering))
        i2 = random.randint(0, len(ordering))
        if i1 == i2:
            continue

        n1, n2 = ordering[i1], ordering[i2]
        if i1 < i2:
            dag.add_edge(n1, n2)
        else:
            dag.add_edge(n2, n1)
        num_added += 1
