from satispy import Variable, Cnf
from copy import deepcopy
import utils, math, random
import gutils as gu
import pycosat as ps
import networkx as nx


# ====================
# PycoSat Reduction
# ====================

class LiteralTranslator(object):
    """
    A helper class for integration with PycoSat, allows for two-way translation
    between string literal and its index representation. Example:

    lt = LiteralTranslator()
    key = lt.touch_literal("Harry < Hermione")
    lt.translate(key)                       # "Harry < Hermione"
    lt.touch_literal("Harry < Hermione")    # `key`
    """
    def __init__(self, constraints, shuffle=False):
        self.counter = 1
        self.literal_to_key = {}
        self.key_to_literal = {}

        self.shuffle = shuffle
        if shuffle:
            self.constraints = random.shuffle(constraints)
        else:
            self.constraints = constraints
        # Do a base scan of all constraints.
        self.__process_constraints(constraints)

    def __process_constraints(self, constraints):
        for constraint in constraints:
            a, b, c = constraint
            self.touch_literal('%s < %s' % (a, c))
            self.touch_literal('%s < %s' % (c, a))
            self.touch_literal('%s < %s' % (b, c))
            self.touch_literal('%s < %s' % (c, b))

    def __add_literal(self, literal):
        assert(literal not in self.literal_to_key)

        self.literal_to_key[literal] = self.counter
        self.key_to_literal[self.counter] = literal
        self.counter += 1
        return self.literal_to_key[literal]

    def __add_literals(self, literals):
        for literal in literals:
            if not literal in self.literal_to_key:
                self.__add_literal(literal)

    def touch_literal(self, literal):
        """
        Add literal if it does not exist, then return its original or newly created key.
        :param literal: literal of form "Snape < Dumbledore"
        :return: a positive integer signifying its index
        """
        if literal in self.literal_to_key:
            return self.literal_to_key[literal]

        return self.__add_literal(literal)

    def find_literal(self, literal):
        if literal in self.literal_to_key:
            return self.literal_to_key[literal]
        return None

    def translate(self, key):
        """
        :param key: index of string literal
        :return: string literal corresponding to `key`
        """
        if key not in self.key_to_literal:
            return LookupError
        return self.key_to_literal[key]

    def literals(self):
        return self.literal_to_key.keys()

    def reset(self):
        self.literal_to_key.clear()
        self.key_to_literal.clear()
        self.counter = 1
        if self.shuffle:
            self.constraints = random.shuffle(self.constraints)
        self.__add_literals(self.constraints)


class LiteralTransitivityManager(object):
    """
    Helper class to enforce dependencies based on constraints.
    Keeps a list of wizards and literal dependencies. Needs a LiteralTranslator object.

    Ltm = LiteralTransitivityManager(L)
    transitivity_constraints = Ltm.enforce()
    cnf.extend(transitivity_constraints)
    """
    def __init__(self, lt):
        self.lt = lt
        self.dependencies = {}
        self.clauses = set()

        self.__process_dependencies()

    def __process_dependencies(self):
        for lit in self.lt.literals():
            x, y = lit.split(' < ')
            self.__add_dependency(x, y)

    def __add_dependency(self, x, y):
        """
        If x < y, add x as a dependency of y.
        """
        if y not in self.dependencies:
            self.dependencies[y] = set()
        self.dependencies[y].add(x)

    def __enforce_dependencies(self, literal):
        """
        If z < x and y < z, then y < x for all y.
        :param literal: string in form 'z < x'
        :return: cnf clauses to enforce transitivity on literal
        """
        z, x = literal.split(' < ')
        for y in self.dependencies[z]:
            z_x = self.lt.touch_literal('%s < %s' % (z , x))
            y_z = self.lt.touch_literal('%s < %s' % (y , z))
            y_x = self.lt.touch_literal('%s < %s' % (y , x))
            constraint = (-z_x, -y_z, y_x)

            self.__add_dependency(y, x)
            self.clauses.add(constraint)

    def constraints(self, num_iter=None, restart=False):
        """
        The dependency chain assures that transitivity constraints
        are satisfied.
        :return: cnf clauses to enforce transitivity for all literals
        """
        if restart:
            self.clauses.clear()

        size = -1
        if num_iter:
            for literal in self.lt.literals():
                self.__enforce_dependencies(literal)
                # Terminate if size does not change, .i.e. no updates
                if size == len(self.clauses):
                    return self.clauses

                size = len(self.clauses)

            return self.clauses

        while not len(self.clauses) == size:
            size = len(self.clauses)
            for literal in self.lt.literals():
                self.__enforce_dependencies(literal)

        return self.clauses


class LiteralConsistencyManager(object):
    def __init__(self, lt):
        self.lt = lt

    def constraints(self):
        clauses = []
        for lit in self.lt.literals():
            z, x = lit.split(' < ')
            negation = x + ' < ' + z
            n = self.lt.find_literal(negation)
            if not n:
                continue

            m = self.lt.find_literal(lit)
            # Both cannot be true.
            constraint = [-n, -m]
            clauses.append(constraint)

        return clauses


def __scan_clauses_pycosat(constraints, lt):
    cnf = []
    for constraint in constraints:
        a, b, c = constraint
        x1 = lt.touch_literal('%s < %s' % (a, c))
        x2 = lt.touch_literal('%s < %s' % (c, a))
        x3 = lt.touch_literal('%s < %s' % (b, c))
        x4 = lt.touch_literal('%s < %s' % (c, b))
        cnf.append([x1, x2])
        cnf.append([x3, x4])
        cnf.append([-x1, -x4])
        cnf.append([-x2, -x3])

    return cnf


def reduce_pycosat(constraints, lt):
    """
    :param constraints:
    :param lt: a LiteralTranslator object
    :return: normal form in Pycosat spec
    """
    cnf = __scan_clauses_pycosat(constraints, lt)

    T = LiteralTransitivityManager(lt)
    t_constraints = T.constraints()
    cnf.extend(t_constraints)

    C = LiteralConsistencyManager(lt)
    c_constraints = C.constraints()
    cnf.extend(c_constraints)

    return cnf


def run_pycosat(cnf):
    return ps.solve(cnf)


def translate_pycosat(solution, lt):
    """
    Returns a list of string literals, i.e. ["Harry < Hermione", "Hermione < Dumbledore"]
    :param solution: solution in Pycosat spec
    :param lt: same LiteralTranslator object used for reduction
    :return: literals that are true
    """
    literals = []
    for key in solution:
        if key > 0:
            literals.append(lt.translate(key))

    return literals


def solve_pycosat(constraints):
    lt = LiteralTranslator(constraints)
    cnf = reduce_pycosat(constraints, lt)
    sat = run_pycosat(cnf)
    assignments = translate_pycosat(sat, lt)

    # Deterministic reduction. Solution must be a DAG or cannot exist.
    dag = gu.build_graph(assignments)
    return gu.linearize(dag)

# ========================
# Pycosat Randomized
# ========================


# How many transitivity scans we do in the next iteration if current one fails.
TRANSITIVITY_KICK_FACTOR = 1.5


class SimulatedAnnealingReduction(object):
    """
    Solution gives an ordering of wizards that satisfies all constraints.

    R = SimulatedAnnealingReduction(constraints)
    solution = R.solve()
    """
    def __init__(self, constraints):
        self.constraints = constraints
        self.t = len(constraints)

    def cost(self, solution):
        return len(self.constraints) - \
               utils.num_constraints_satisfied(self.constraints, solution)

    def search_neighborhood(self, solution):
        """
        Randomized search in the neighborhood of number of scans.
        :param solution: original solution
        :return: solution with new number of scans
        """
        return NotImplementedError

    def solve(self):
        solution = self._Solution([], 1)
        while not utils.check(self.constraints, solution.ordering):
            # Find solution s' in neighborhood of s
            solution_p = self.search_neighborhood(solution)
            delta = self.cost(solution_p) - self.cost(solution)
            if delta < 0:
                solution = solution_p
            else:
                r = math.e ** (- delta / self.t)
                if random.random() < r:
                    solution = solution_p
            # Anneal by decreasing probability T.
            self.t = self.t * 0.8

        return solution.ordering

    class _Solution(object):
        def __init__(self, ordering, num_scans):
            self.ordering = ordering
            self.num_scans = num_scans


def solve_pycosat_randomize(constraints):
    lt = LiteralTranslator(constraints)
    cnf = __scan_clauses_pycosat(constraints, lt)

    num_scans = 2
    solution = []
    while not utils.check(constraints, solution):
        T = LiteralTransitivityManager(lt)
        t_constraints = T.constraints(num_iter=num_scans)
        C = LiteralConsistencyManager(lt)
        c_constraints = C.constraints()
        sat_clauses = cnf + list(t_constraints) + c_constraints

        sat = run_pycosat(sat_clauses)

        assignments = translate_pycosat(sat, lt)
        G = gu.build_graph(assignments)
        if nx.is_directed_acyclic_graph(G):
            solution = gu.linearize(G)
        else:
            solution = gu.extract_linearize(G)

        num_scans = int(math.ceil(num_scans * TRANSITIVITY_KICK_FACTOR))

    return solution

# ====================
# Satispy Reduction
# ====================


def touch_variable(name, map):
    """
    Find variable map[name] if it exists else create one and map it.
    :param name: key to mapper
    :param map: mapping of name to Variable
    :return: variable found or created
    """
    if name in map:
        var = map[name]
    else:
        var = Variable(name)
        map[name] = var
    return var


def reduce_satispy(constraints):
    """
    Reduce constraints from wizards problem into CNF form for our SAT instance.
    :param constraints: inputs from wizard problem
    :return: Cnf object
    """
    mapping = {}
    exp = Cnf()
    for constraint in constraints:
        a, b, c = constraint
        x_1 = touch_variable('%s < %s' % (a, c), mapping)
        x_2 = touch_variable('%s < %s' % (c, a), mapping)
        x_3 = touch_variable('%s < %s' % (b, c), mapping)
        x_4 = touch_variable('%s < %s' % (c, b), mapping)

        exp &= (x_1 | x_2) & (x_3 | x_4) & (-x_1 | -x_4) & (-x_2 | -x_3)

    return exp
