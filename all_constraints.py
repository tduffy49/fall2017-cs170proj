import random
import sys

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
    for i in range(n):
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

def randomly_select_all_wizards(constraints, n):
    lst = list(constraints)
    if(not all_wizards(constraints, n)):
        return randomly_select_constraints(generate_all_constraints(range(1, n+1)), n)
    return lst


def find_duplicates1(constraints, n):
    """
    From randomly picked (a, b, c) create duplicate of type (a, a, c)

    :param constraints: list of constraints in form [ (a, b, c) .... ]
    :param n: number of duplicate constraints to find
    :return: `n`-sized list of duplicates
    """
    c = list(constraints)
    duplicates = []
    for _ in range(n):
        i = random.randint(0, len(c))
        elem = c.pop(i)
        duplicates.append((elem[0], elem[0], elem[2]))
    return duplicates

def find_duplicates2(constraints, n):
    """
     From randomly picked (a, b, c) create duplicate of type (a, c, c)

     :param constraints: list of constraints in form [ (a, b, c) .... ]
     :param n: number of duplicate constraints to find
     :return: `n`-sized list of duplicates
     """
    c = list(constraints)
    duplicates = []
    for _ in range(n):
        i = random.randint(0, len(c))
        elem = c.pop(i)
        duplicates.append((elem[0], elem[2], elem[2]))
    return duplicates

def find_duplicates3(constraints, n):
    """
     From randomly picked (a, b, c) create duplicate of type (a, c, a)

     :param constraints: list of constraints in form [ (a, b, c) .... ]
     :param n: number of duplicate constraints to find
     :return: `n`-sized list of duplicates
     """
    c = list(constraints)
    duplicates = []
    for _ in range(n):
        i = random.randint(0, len(c))
        elem = c.pop(i)
        duplicates.append((elem[0], elem[2], elem[0]))
    return duplicates

def find_duplicates4(constraints, n):
    """
     From randomly picked (a, b, c) create duplicates of type (a, a, a)

     :param constraints: list of constraints in form [ (a, b, c) .... ]
     :param n: number of duplicate constraints to find
     :return: `n`-sized list of duplicates
     """
    c = list(constraints)
    duplicates = []
    for _ in range(n):
        i = random.randint(0, len(c))
        elem = c.pop(i)
        duplicates.append((elem[0], elem[0], elem[0]))
    return duplicates

def inject_duplicates(constraints, n, form):
    for i in range(n):
        index = random.randint(0, len(constraints))
        triplet = constraints[index]
        i, j, k = form
        constraints[index] = (triplet[i], triplet[j], triplet[k])
    
def inject_all_duplicates(constraints):
    for form in [(0, 0, 2), (0, 2, 2), (0, 2, 0), (0, 0, 0)]:
        inject_duplicates(constraints, int(len(constraints) * 0.05), form)
    
def main():
    if len(sys.argv) < 3:
        print('Usage: python all_constraints.py <length of list> <number of constraints>')
        return

    lst_length = int(sys.argv[1])
    num_constraints = int(sys.argv[2])
    
    all_possibilities = generate_all_constraints(range(lst_length))
    constraints = randomly_select_constraints(all_possibilities, num_constraints)
    while (not all_wizards(constraints, lst_length)):
        constraints = randomly_select_constraints(all_possibilities, num_constraints)

    inject_all_duplicates(constraints)

    for c in constraints:
        print(c)
    print(len(constraints))

main()
    
    
    
