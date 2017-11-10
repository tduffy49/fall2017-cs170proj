from random import *
import string
def constraintGenNoDupes(n, numConstraints):
    """
    input: n (list) - a list of ordered elements from [0 .. n) increments of 1
            e.g. [0, 1, 2, 3, 4] for n = 5
    input : numConstraints (int) - the number of constraints to form from n
    ouput : a map of constraints of (first, second) : third where third is not
            between first and second. first, second cannot be duplicated pairs
            in the constraints
    """
    constraints = dict()
    rand = Random()

    while(len(constraints) < numConstraints):
        first = rand.randrange(len(n))
        second = rand.randrange(len(n))
        third = rand.randrange(len(n))

        if(first <= third and second <= third or first >= third and second >= third):
            constraints[(first, second)] = third

    #make sure every element in n is used at least once
    s = set()
    for c in constraints:
        s.add(c[0])
        s.add(c[1])
        s.add(constraints[c])
    if(len(s) != len(n)):
        print("Constraints are not valid! Missing elements from n {0}/{1}".format(len(s), len(n)))
        constraints = constraintGenNoDupes(n, numConstraints)

    constraints = [[c[0], c[1], constraints[c]] for c in constraints]

    return constraints

def constraintGenDupes(n, numConstraints):
    """
    input: n (list) - a list of ordered elements from [0 .. n) increments of 1
            e.g. [0, 1, 2, 3, 4] for n = 5
    input : numConstraints (int) - the number of constraints to form from n
    ouput : a list of list of constraints [first, second, third] : where third is not between first and second. first,second can be duplicated pairs in the constraints
    """
    constraints = []
    rand = Random()

    while(len(constraints) < numConstraints):
        first = rand.randrange(len(n))
        second = rand.randrange(len(n))
        third = rand.randrange(len(n))

        if(first <= third and second <= third or first >= third and second >= third):
            constr = [first, second, third]
            if(constr not in constraints):
                constraints.append(constr)

    #make sure every element in n is used at least once
    s = set()
    for c in constraints:
        s.add(c[0])
        s.add(c[1])
        s.add(c[2])
    if(len(s) != len(n)):
        print("Constraints are not valid! Missing elements from n {0}/{1}".format(len(s), len(n)))
        constraints = constraintGenDupes(n, numConstraints)

    return constraints

def nameGen(constraints, n):
    """
    input: constraints - list of lists of [first, second, third] (all ints)
    output: Returns a tuple
            element 0 : an ordered list of the new name mappings
            element 1 : new list with each distinct integer within a range [0, n) in constraints converted into a distinct random name
    """

    asciiVals = "{0}{1}".format(string.ascii_letters, string.digits)
    names = []
    rand = Random()
    newNames = []

    while len(names) < n:
        name = []
        nameSize = rand.randrange(1,11)
        for letter in range(nameSize):
            name.append(asciiVals[rand.randrange(len(asciiVals))])
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
