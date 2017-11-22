from satispy import Variable, Cnf
import pycosat as ps

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
    def __init__(self):
        self.counter = 1
        self.literal_to_key = {}
        self.key_to_literal = {}

    def __add_literal(self, literal):
        assert(literal not in self.literal_to_key)

        self.literal_to_key[literal] = self.counter
        self.key_to_literal[self.counter] = literal
        self.counter += 1
        return self.literal_to_key[literal]

    def __add_literals(self, literals):
        for literal in literals:
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
        self.clauses = []           # Transitivity clauses to be added.

    def __scan(self):
        for lit in self.lt.literals():
            young_wiz, old_wiz = lit.split(' < ')
            if old_wiz not in self.dependencies:
                self.dependencies[old_wiz] = set()
            self.dependencies[old_wiz].add(young_wiz)

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
            constraint = [-z_x, -y_z, y_x]
            # TODO: Add dependency update
            if constraint not in self.clauses:
                self.clauses.append(constraint) # If z_x and y_z, then y_x

    def enforce(self):
        """
        The dependency chain assures that transitivity constraints
        are satisfied.
        :return: cnf clauses to enforce transitivity for all literals
        """
        self.__scan()
        size = -1
        while not len(self.clauses) == size:
            size = len(self.clauses)
            for literal in self.lt.literals():
                self.__enforce_dependencies(literal)

        return NotImplementedError # Class not tested and proved.

class LiteralConsistencyManager(object):
    def __init__self(self, lt):
        return NotImplementedError

def reduce_pycosat(constraints, lt):
    """
    :param constraints:
    :param lt: a LiteralTranslator object
    :return: normal form in Pycosat spec
    """
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

def solve_pycosat(cnf):
    return ps.solve(cnf)

def translate_pycosat(solution, lt):
    """
    Returns a list of string literals, i.e. ["Harry < Hermione", "Hermione < Dumbledore"]
    :param solution: solution in Pycosat spec
    :param lt: same LiteralTranslator object used for reduction
    :return: list of string literals inequalities
    """
    literals = []
    for key in solution:
        if key > 0:
            literals.append(lt.translate(key))

    return literals

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
