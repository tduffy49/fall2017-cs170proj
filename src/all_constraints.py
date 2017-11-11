import random

def generate_all_constraints(lst):
    """
    Generate all constraints where (a, b, c) means c not between a and b in `lst`,
    but does not include duplicates of type (a, a, b) (a, b, a) (a, a, a), (b, a, a).

    :param lst: ordered list for us to generate constraints
    :return: all constraints with no duplicates of types above
    """
    constraints = []
    for i in range(len(lst)):
        for j in range(i):
            for k in range(j):
                rand = random.random()  # Add one or the other.
                if (rand > 0.5):
                    constraints.append((lst[k], lst[j], lst[i]))
                else:
                    constraints.append((lst[j], lst[k], lst[i]))
        for j in range(i + 1, len(lst)):
            for k in range(i + 1, j):
                rand = random.random()
                if rand > 0.5:
                    constraints.append((lst[k], lst[j], lst[i]))
                else:
                    constraints.append((lst[j], lst[k], lst[i]))
    return constraints

def randomly_select_constraints(constraints, n):
    """
    :param constraints: the list of 3-element constraint tuples
    :param n: number of constraints selected
    :return: n-sized list of randomly picked elements from `constraints`
    """
    constraints_copy = list(constraints)
    selected = []
    for _ in range(n):
        index = random.randrange(len(constraints_copy))
        c = constraints_copy.pop(index)
        selected.append(c)
    return selected

def all_wizards(constraints, n):
    """
    input: n(int) number of unique wizards
    input: constraints(list of 3 element lists): selected constraints
    output: true if all wizards are accounted for, false otherwise
    """
    s = set()
    for c in constraints:
        s.add(c[0])
        s.add(c[1])
        s.add(c[2])
    if(len(s) != n):
        return False
    return True

DUPLICATE_FORMS = [(0, 0, 2), (0, 2, 2), (0, 2, 0), (0, 0, 0)]

def insert_random(lst, elem):
    """
    DOES NOT MUTATE `lst`
    :param lst: list to be added to
    :param elem: element to be added
    :return: new list with `elem` added randomly
    """
    l = list(lst)
    i = random.randrange(len(lst))
    l.insert(i, elem)
    return l

def insert_duplicates(constraints, n):
    """
    DOES NOT MUTATE `constraints`
    :param constraints: Constraints to
    :param n:
    :return: new list
    """
    c = list(constraints)
    for i in range(n):
        rand = random.randrange(len(constraints))
        triplet = constraints[rand]
        i, j, k = DUPLICATE_FORMS[random.randrange(len(DUPLICATE_FORMS))]
        c = insert_random(c, (triplet[i], triplet[j], triplet[k]))
    return c
