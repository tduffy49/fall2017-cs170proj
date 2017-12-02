from satispy import Variable, Cnf
from copy import deepcopy
import utils, math, random
import gutils as gu
import pycosat as ps
import networkx as nx


# ============================
# PycoSat Reduction Objects
# ============================

class LiteralTranslator(object):
    """
    A helper class for integration with PycoSat, allows for two-way translation
    between string literal and its index representation. A literal can be in two
    forms, (1) inequality form, i.e. [ "Dumbledore < Harry" ] and (2) key form,
    i.e [ (x1, x2), (-x3, x2) ]. Inequalities are referred to as `literals` and
    keys as `keys`. Usage example:

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
            self._constraints = random.shuffle(constraints)
        else:
            self._constraints = constraints
        # Do a base scan of all constraints.
        self.__add_constraints(constraints)

    def __add_constraints(self, constraints):
        for constraint in constraints:
            a, b, c = constraint
            self.touch_inequality('%s < %s' % (a, c))
            self.touch_inequality('%s < %s' % (c, a))
            self.touch_inequality('%s < %s' % (b, c))
            self.touch_inequality('%s < %s' % (c, b))

    def __add_inequality(self, literal):
        assert(literal not in self.literal_to_key)

        self.literal_to_key[literal] = self.counter
        self.key_to_literal[self.counter] = literal
        self.counter += 1
        return self.literal_to_key[literal]

    def __add_inequalities(self, literals):
        for literal in literals:
            if not literal in self.literal_to_key:
                self.__add_inequality(literal)

    def touch_inequality(self, literal):
        """
        Add literal if it does not exist, then return its original or newly created key.
        :param literal: literal of form "Snape < Dumbledore"
        :return: a positive integer signifying its index
        """
        if literal in self.literal_to_key:
            return self.literal_to_key[literal]

        return self.__add_inequality(literal)

    def inequality_to_key(self, literal):
        if literal in self.literal_to_key:
            return self.literal_to_key[literal]
        return None

    def key_to_inequality(self, key):
        """
        :param key: index of string literal
        :return: string literal corresponding to `key`
        """
        if key not in self.key_to_literal:
            return LookupError
        return self.key_to_literal[key]

    def inequalities(self):
        return self.literal_to_key.keys()

    def base_clauses(self):
        cnf = set()
        for constraint in self._constraints:
            a, b, c = constraint
            x1 = self.inequality_to_key('%s < %s' % (a, c))
            x2 = self.inequality_to_key('%s < %s' % (c, a))
            x3 = self.inequality_to_key('%s < %s' % (b, c))
            x4 = self.inequality_to_key('%s < %s' % (c, b))
            if not x1 or not x2 or not x3 or not x4:
                return LookupError

            cnf.add((x1, x2))
            cnf.add((x3, x4))
            cnf.add((-x1, -x4))
            cnf.add((-x2, -x3))

        return cnf


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
        for lit in self.lt.inequalities():
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
            z_x = self.lt.touch_inequality('%s < %s' % (z , x))
            y_z = self.lt.touch_inequality('%s < %s' % (y , z))
            y_x = self.lt.touch_inequality('%s < %s' % (y , x))
            constraint = (-z_x, -y_z, y_x)

            self.__add_dependency(y, x)
            self.clauses.add(constraint)

    def constraints(self, num_iter=None):
        """
        The dependency chain assures that transitivity constraints
        are satisfied.
        :return: cnf clauses to enforce transitivity for all literals
        """
        size = -1
        if num_iter:
            while True:
                for literal in self.lt.inequalities():
                    self.__enforce_dependencies(literal)

                    num_iter -= 1
                    if num_iter < 0:
                        return self.clauses

                # Terminate if size does not change for 1 whole scan, .i.e. no updates
                if size == len(self.clauses):
                    return self.clauses
                size = len(self.clauses)

        while not len(self.clauses) == size:
            size = len(self.clauses)
            for literal in self.lt.inequalities():
                self.__enforce_dependencies(literal)

        return list(self.clauses)


class LiteralConsistencyManager(object):
    def __init__(self, lt):
        self.lt = lt

    def all_constraints(self):
        clauses = set()
        for lit in self.lt.inequalities():
            z, x = lit.split(' < ')
            negation = x + ' < ' + z
            n = self.lt.inequality_to_key(negation)
            if not n:
                continue

            m = self.lt.inequality_to_key(lit)
            # Both cannot be true.
            constraint = (-n, -m)
            clauses.add(constraint)

        return list(clauses)

    def constraints(self, cnf):
        clauses = set()
        for clause in cnf:
            for key in clause:
                literal = self.lt.key_to_inequality(abs(key))
                z, x = literal.split(' < ')
                negation = x + ' < ' + z
                n = self.lt.inequality_to_key(negation)
                if not n:
                    continue

                m = self.lt.inequality_to_key(literal)
                # Both cannot be true.
                constraint = (-n, -m)
                clauses.add(constraint)

        return list(clauses)


LESS_THAN_DELIMITER = ' < '

class ConstraintManager(object):
    def __init__(self, translator):
        """
        :param translator: a LiteralTranslator object
        """
        self.translator = translator

    @staticmethod
    def __process_dependencies(translator, dependencies, clauses):
        """
        :param dependencies: dict
        :param clauses: CNF clauses
        :return: mutated `dependencies` dict
        """
        for clause in clauses:
            for key in clause:
                literal = translator.key_to_inequality(abs(key))
                x, y = literal.split(LESS_THAN_DELIMITER)
                ConstraintManager.__add_dependency(dependencies, x, y)

        return dependencies

    @staticmethod
    def __add_dependency(dependencies, x, y):
        """
        If x < y, add x as a dependency of y to `dependencies`
        :param dependencies: dict
        :param x: smaller
        :param y: bigger
        :return: mutated `dependencies` dict
        """
        if y not in dependencies:
            dependencies[y] = set()
        dependencies[y].add(x)

        return dependencies

    @staticmethod
    def __dependency_constraints(translator, dependencies, literal):
        """
        If z < x and y < z, then y < x for all y.
        :param translator: a LiteralTranslator object
        :param dependencies: dict
        :param literal: string in form 'z < x'
        :return: set of cnf clauses to enforce transitivity on literal
        """
        clauses = set()
        z, x = literal.split(LESS_THAN_DELIMITER)
        for y in dependencies[z]:
            z_x = translator.touch_inequality('%s < %s' % (z, x))
            y_z = translator.touch_inequality('%s < %s' % (y, z))
            y_x = translator.touch_inequality('%s < %s' % (y, x))
            constraint = (-z_x, -y_z, y_x)

            ConstraintManager.__add_dependency(dependencies, y, x)
            clauses.add(constraint)

        return clauses

    @staticmethod
    def __inequalities_in_(translator, clauses):
        literals = set()
        for clause in clauses:
            for key in clause:
                literal = translator.key_to_inequality(abs(key))
                literals.add(literal)

        return literals

    def transitivity_constraints(self, clauses, num_required=None, num_iter=None):
        """
        :param clauses: [ (x1, -x2, x3) ] literals in key form
        :param num_required: number of unique transitivity constraints required, may
        output below this number if scans finished
        :param num_iter: number of total scans
        :return: set of clauses enforcing transitivity
        """
        result = set()
        dependencies = self.__process_dependencies(
            self.translator, dict(), clauses
        )
        size, i = -1, 0
        while size != len(result):
            size = len(result)
            for literal in self.translator.inequalities():
                new_clauses = ConstraintManager.__dependency_constraints(
                    self.translator, dependencies, literal
                )
                result = result.union(new_clauses)

                # return if result has more clauses than num_required
                if num_required and len(result) >= num_required:
                    return result
            i += 1
            if not i < num_iter:
                return result

        return result

    def consistency_constraints(self, clauses):
        """
        :param clauses: list of clauses in cnf form
        :return: set of clauses enforcing consistency
        """
        result = set()
        for clause in clauses:
            for key in clause:
                literal = self.translator.key_to_inequality(abs(key))
                z, x = literal.split(' < ')
                negation = x + ' < ' + z
                n = self.translator.inequality_to_key(negation)
                if not n:
                    continue

                m = self.translator.inequality_to_key(literal)
                # Both cannot be true.
                constraint = (-n, -m)
                result.add(constraint)

        return result

# ========================
# Pycosat Reduction API
# ========================

def reduce_pycosat(constraints):
    """
    :param constraints: [ (w1, w2, w3) ]
    :param lt: a LiteralTranslator object
    :return: list of clauses in normal form
    """
    L = LiteralTranslator(constraints)
    result = L.base_clauses()

    C = ConstraintManager(L)
    result = result.union(C.transitivity_constraints(list(result)))
    result = result.union(C.consistency_constraints(list(result)))

    return list(result)


def run_pycosat(cnf):
    """
    :param cnf: clauses in normal form
    :return: satisfying assignments
    """
    return ps.solve(cnf)


def translate_assignments(assignments, lt):
    literals = []
    for key in assignments:
        if key > 0:
            literals.append(lt.key_to_inequality(key))

    return literals

def translate_pycosat(assignments, lt, deterministic=True):
    """
    :param assignments: assignments from SAT solver
    :param lt: same LiteralTranslator object used for reduction
    :param deterministic: if True, input is deterministically a DAG
    :return: wizard ordering
    """
    literals = translate_assignments(assignments, lt)

    G = gu.build_graph(literals)
    if deterministic:
        return gu.linearize(G)

    if nx.is_directed_acyclic_graph(G):
        assignments = gu.linearize(G)
    else:
        dag = gu.extract_max_dag(G)
        assignments = gu.linearize(dag)
    return assignments


def solve_pycosat(constraints):
    """
    :param constraints: [ (w1, w2, w3) ]
    :return: wizard ordering that satisfies all constraints
    """
    lt = LiteralTranslator(constraints)
    cnf = reduce_pycosat(constraints)
    sat = run_pycosat(cnf)
    solution = translate_pycosat(sat, lt)

    # Deterministic reduction. Solution must be a DAG or cannot exist.
    return solution


# ========================
# Pycosat Randomized
# ========================

class SimulatedAnnealing(object):
    """
    An instance of SimulatedAnnealing problem
    """
    def __init__(self, problem):
        self.problem = problem
        self.t = self.initial_anneal()

    def initial_anneal(self):
        pass

    def initial_solution(self):
        pass

    def is_valid(self, solution):
        pass

    def cost(self, solution):
        pass

    def search_neighborhood(self, solution):
        pass

    anneal_reduction_factor = 0.9

    def solve(self, num_iter=None):
        """
        :param num_iter: Number of iterations until solution returned.
        May not be a valid solution.
        :return:
        """
        solution = self.initial_solution()
        while not self.is_valid(solution):
            solution_p = self.search_neighborhood(solution)
            delta = self.cost(solution_p) - self.cost(solution)
            if delta < 0:
                solution = solution_p
            else:
                r = math.e ** (- delta / self.t)
                if random.random() < r:
                    solution = solution_p
            self.t = self.t * self.anneal_reduction_factor

        return solution


class GraphAnnealing(SimulatedAnnealing):
    """
    Anneals the graph DAG extraction.
    """
    def initial_anneal(self):
        return 1.0

    def initial_solution(self):
        G = gu.build_graph(self.problem.literals)
        dag = gu.extract_max_dag(G)
        ordering = gu.linearize(dag)

        return self._Solution(dag, ordering)

    def is_valid(self, solution):
        return utils.check(self.problem.constraints, solution.ordering)

    def cost(self, solution):
        """
        :param solution: _Solution
        :return: non-negative float
        """
        return len(self.problem.constraints) \
               - utils.num_constraints_satisfied(self.problem.constraints, solution.ordering)

    edge_retain_factor = 0.9

    def search_neighborhood(self, solution):
        """
        Retain a portion of edges to maintain solution in neighborhood.
        Create new edges randomly while still maintaining a DAG.
        :param solution: _Solution
        :return: _Solution in neighborhood of `solution`
        """
        G = gu.build_graph(self.problem.literals)
        edges_retained = random.sample(
            list(solution.graph.edges()), int(solution.graph.number_of_edges()
                                              * self.edge_retain_factor)
        )

        dag_p = nx.DiGraph()
        dag_p.add_nodes_from(G)
        dag_p.add_edges_from(edges_retained)

        ordering_p = gu.linearize(dag_p)
        gu.add_random_edges(dag_p, solution.graph.number_of_edges() - len(edges_retained))

        return self._Solution(dag_p, ordering_p)

    class _Problem(object):
        """
        Given a list of strings [ "w1 < w2" ], construct a DAG
        out of them.
        """
        def __init__(self, literals, constraints):
            """
            :param literals: [ "w1 > w2" ]
            :param constraints: [ (w1, w2, w3) ]
            """
            self.literals = literals
            self.constraints = constraints

    class _Solution(object):
        def __init__(self, graph, ordering):
            self.graph = graph
            self.ordering = ordering


class SimulatedAnnealingReduction(object):
    """
    Solution gives an ordering of wizards that satisfies all constraints.

    R = SimulatedAnnealingReduction(constraints)
    ordering = R.solve()
    """
    def __init__(self, constraints):
        """
        :param constraints: [ (w1, w2, w3) ]
        """
        self.constraints = constraints
        self.t = float(self._initial_anneal())
        self.translator = LiteralTranslator(constraints)

    def _initial_anneal(self):
        return float(len(self.constraints))

    def cost(self, solution):
        """
        Cost is considered a 'badness' metric, here measured in the number of unsatisfied constraints.
        :param solution: _Solution object
        :return: cost of `solution`
        """
        return len(self.constraints) - \
               utils.num_constraints_satisfied(self.constraints, solution.ordering)

    def __rand_choose(self, elements, probs):
        """
        Choose element in elements with probability corresponding to array assigned.
        :param elements: elements to choose from
        :param probs: probabilities array that adds to 1
        :return: element chosen
        """
        assert(len(elements) == len(probs))
        assert(sum(probs) == 1)

        r = random.random()
        cum_probs = []
        for i in range(len(probs)):
            cum_probs.append(sum(probs[:i + 1]))
        for i in range(len(cum_probs)):
            if r > cum_probs[i] and i <= cum_probs[i + 1]:
                return elements[i]

        return RuntimeError

    def __compute_retain_factor(self, solution):
        return 1 - math.e ** (- utils.num_constraints_satisfied(self.constraints, solution.ordering) / self.t)

    # Neighborhood search heuristics.
    T_CLAUSES_RETAIN_FACTOR = 0.98              # Retained clauses has to be less than scan decrease factor
    NUM_T_CLAUSES_CAP = 200000                  # Maximum number of transitivity clauses

    def search_neighborhood(self, solution, all_t_clauses):
        """
        Randomized search in the neighborhood of solution characteristics. Heuristics comprise
        of in order of importance:
        1. transitivity SAT clauses
        2. number of transitivity clauses
        :param solution: s
        :return: neighboring s' to s according to heuristics.
        """
        L = self.translator
        base_clauses = list(L.base_clauses())
        C = LiteralConsistencyManager(L)
        # Number of transitivity clauses fixed always.
        num_t_clauses_p = min(len(all_t_clauses), self.NUM_T_CLAUSES_CAP)

        # Allow neighborhood search by constraints kept.
        t_clauses_retained = random.sample(
            solution.t_clauses,
            int(min(num_t_clauses_p * self.__compute_retain_factor(solution), len(solution.t_clauses)))
        )
        t_clauses_p = t_clauses_retained + \
            random.sample(all_t_clauses,
                          min(num_t_clauses_p - len(t_clauses_retained), len(all_t_clauses)))

        clauses_p = base_clauses + t_clauses_p
        clauses_p += list(C.constraints(clauses_p))
        print 'SAT all clauses: ' + str(len(clauses_p))
        assignments = run_pycosat(clauses_p)
        ordering = translate_pycosat(assignments, L, deterministic=False)

        solution_p = self._Solution(ordering, t_clauses_p)

        return solution_p

    # Simulated annealing factor, analogous to cooling glass (gets more rigid over time).
    ANNEAL_FACTOR = 0.9
    NUM_ITER_ANNEAL_RESET = 10000

    def solve(self):
        """
        :return: list of wizards in order that satisfies ALL constraints
        """
        # Solve for all constraints
        T = LiteralTransitivityManager(self.translator)
        all_t_constraints = T.constraints()

        solution = self._Solution([], [])
        while not utils.check(self.constraints, solution.ordering):
            # Find solution s' in neighborhood of s. Adjust retain factor according
            # to anneal factor.
            solution_p = self.search_neighborhood(solution, all_t_constraints)
            delta = self.cost(solution_p) - self.cost(solution)
            if delta < 0:
                solution = solution_p
            else:
                r = math.e ** (- delta / float(self.t))
                if random.random() < r:
                    solution = solution_p

            # Anneal by decreasing probability T.
            self.t = self.t * self.ANNEAL_FACTOR

        return solution.ordering

    class _Solution(object):
        """
        Shell object for simulated annealing.
        """
        def __init__(self, ordering, t_clauses):
            """
            :param ordering: wizard ordering
            :param t_clauses: transitivity clauses
            """
            self.ordering = ordering
            self.t_clauses = t_clauses

NUM_PYCOSAT_LITERALS_CAP = 300000

def solve_pycosat_annealing(constraints):
    L = LiteralTranslator(constraints)
    T = LiteralTransitivityManager(L)
    C = LiteralConsistencyManager(L)

    t_clauses = T.constraints()
    t_clauses = t_clauses[:min(len(t_clauses), NUM_PYCOSAT_LITERALS_CAP)]
    all_clauses = list(L.base_clauses()) + list(t_clauses)
    all_clauses += C.constraints(all_clauses)
    assignments = run_pycosat(all_clauses)

    p_ga = GraphAnnealing._Problem(translate_assignments(assignments, L), constraints)
    Ga = GraphAnnealing(p_ga)

    return Ga.solve().ordering


# How many transitivity scans we do in the next iteration if current one fails.
TRANSITIVITY_KICK_FACTOR = 4


def solve_pycosat_randomize(constraints):
    """
    Simple randomization solver based on number of scans.
    :param constraints: [ (w1, w2, w3) ]
    :return: wizard ordering that satisfies all constraints
    """
    num_scans = 1
    solution = []
    while not utils.check(constraints, solution):
        lt = LiteralTranslator(constraints)
        cnf = lt.base_clauses()

        T = LiteralTransitivityManager(lt)
        t_constraints = T.constraints(num_iter=num_scans)
        C = LiteralConsistencyManager(lt)
        c_constraints = C.all_constraints()

        sat_clauses = list(cnf) + list(t_constraints) + list(c_constraints)
        sat = run_pycosat(sat_clauses)

        solution = translate_pycosat(sat, lt, deterministic=False)

        num_scans = int(math.ceil(num_scans * TRANSITIVITY_KICK_FACTOR))

    return solution
