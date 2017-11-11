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
                constraints.append((lst[k], lst[j], lst[i]))
                constraints.append((lst[j], lst[k], lst[i]))
    return constraints

def randomly_select_constraints(constraints, n):
    """

    :param constraints: the list of 3-element constraint tuples
    :param n: number of constraints selected
    :return: n-sized list of randomly picked elements from `constraints`
    """
    selected = []
    for i in range(n):
        index = random.randint(0, len(constraints))
        c = constraints.pop(index)
        selected.append(c)
    return selected
<<<<<<< HEAD

constraints = generate_all_constraints(range(1, 51))
random_constraints = randomly_select_constraints(constraints, 500)
for c in random_constraints:
    print(c)

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

def randomly_select_all_wizards(constraints, n):
    lst = list(constraints)
    if(not all_wizards(constraints, n)):
        return randomly_select_constraints(generate_all_constraints(range(1, n+1)), n)
    return lst
=======
>>>>>>> 253ec4a757a4f0385438600c505441d1deabee9d
