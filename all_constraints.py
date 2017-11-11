import random

def generate_all_constraints(lst):
    constraints = []
    for i in range(len(lst)):
        for j in range(i):
            for k in range(j):
                constraints.append((lst[k], lst[j], lst[i]))
                constraints.append((lst[j], lst[k], lst[i]))
        for j in range(i + 1, len(lst)):
            for k in range(i + 1, j):
                constraints.append((lst[k], lst[j], lst[i]))
                constraints.append((lst[j], lst[k], lst[i]))
    return constraints

def randomly_select_constraints(constraints, n):
    selected = []
    for i in range(n):
        index = random.randint(0, len(constraints))
        c = constraints.pop(index)
        selected.append(c)
    return selected

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
