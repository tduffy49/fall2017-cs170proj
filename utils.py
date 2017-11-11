import random
import string

def nameGen(constraints, n):
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

def outputToFile(ordering, constraints, filename):
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
