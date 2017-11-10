from random import *
import string
def constraintGen(n, numConstraints):
    """
    input: n (list) - a list of ordered elements
    input : numConstraints (int) - the number of constraints to form from n
    ouput : a map of constraints (first, second) : third where third is not
            between first and second
    """
    constraints = dict()
    value = None
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
        constraints = constraintGen(n, numConstraints)

    return constraints

def nameGen(constraints, n):
    """
    input: constraints - map of (first, second) : third (all ints)
    output: Returns a tuple
            element 0 : new map with each distinct integer within a range [0, n) in constraints coverted into a distint random name
            element 1 : an ordered list of the new name mappings

    """
    asciiVals = "{0}{1}".format(string.ascii_letters, string.digits)
    names = []
    rand = Random()
    newNames = dict()

    while len(names) < n:
        name = []
        nameSize = rand.randrange(1,11)
        for letter in range(nameSize):
            name.append(asciiVals[rand.randrange(len(asciiVals))])
        if("".join(name) not in names):
            names.append("".join(name))

    for key in constraints:
        newNames[(names[key[0]], names[key[1]])] = names[constraints[key]]

    return newNames , names

def outputToFile(ordering, constraints, filename):
    """
    input: ordering - a list containing the names in proper order
    input: constraints - a map of (first, second) : third constraints
    input: filename - a string with the name of the output file
    output: writes the correct format to filename
    """

    with open(filename, 'w') as f:
        f.write("{0}\n".format(len(ordering)))

        for name in ordering:
            f.write("{0} ".format(name))

        f.write("\n{0}\n".format(len(constraints)))

        for c in constraints:
            f.write("{0} {1} {2}\n".format(c[0], c[1], constraints[c]))
