import random
import string


def check(constraints, solution):
    """
    :param constraints: instance of WizardOrdering
    :param solution: supposed solution
    :return: True if `solution` is valid
    """
    return len(constraints) == num_constraints_satisfied(constraints, solution)


def num_constraints_satisfied(constraints, solution):
    """
    Returns number of constraints satisfied of proposed solution
    :param constraints: [ (w1 w2 w3) ] where w3 not between w1 and w2
    :param solution: ordering of wizards
    :return: number of constraints `solution` satisfied
    """
    if not solution:
        return 0

    result = 0
    for constraint in constraints:
        w1, w2, w3 = constraint
        w1i = solution.index(w1)
        w2i = solution.index(w2)
        w3i = solution.index(w3)
        if (w3i > w2i and w3i > w1i) or (w3i < w2i and w3i < w1i):
            result += 1

    return result


def name_gen(constraints, n):
    """
    input: constraints - list of lists of [first, second, third] (all ints)
    output: Returns a tuple
            element 0 : an ordered list of the new name mappings
            element 1 : new list with each distinct integer within a range [0, n) in constraints converted into a distinct random name
    """

    ascii_vals = "{0}{1}".format(string.ascii_letters, string.digits)
    names = []
    newNames = []

    while len(names) < n:
        name = []
        nameSize = random.randrange(1,11)
        for letter in range(nameSize):
            name.append(ascii_vals[random.randrange(len(ascii_vals))])
        if("".join(name) not in names):
            names.append("".join(name))

    for c in constraints:
        newNames.append([names[c[0]], names[c[1]], names[c[2]]])

    return names, newNames


def output_to_file(ordering, constraints, filename):
    """
    input: ordering - a list containing the names in proper order
    input: constraints - a list of lists of the form [first, second, third]
                        constraints
    input: filename - a string with the name of the output file
    output: writes the correct format to filename
    """

    with open(filename, 'w') as f:
        f.write("{0}\n".format(len(ordering)))

        for name in ordering:
            f.write("{0} ".format(name))

        f.write("\n{0}\n".format(len(constraints)))

        for c in constraints:
            f.write("{0} {1} {2}\n".format(c[0], c[1], c[2]))
