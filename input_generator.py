from instance_validator import main as check
from src import utils
from src.all_constraints import *

DUPLICATE_FRACTION = 0.02       # Fraction of total constraints to be duplicate
NUM_CONSTRAINTS = 500           # Total number of constraints

def main():
    num_main_constraints = int(NUM_CONSTRAINTS * (1 - DUPLICATE_FRACTION))
    num_dup_constraints = NUM_CONSTRAINTS - num_main_constraints
    for lst_length in [20, 35, 50]:
        names, _ = utils.name_gen([], lst_length)

        all_possibilities = generate_all_constraints(names)
        constraints = randomly_select_constraints(all_possibilities, num_main_constraints)
        while (not all_wizards(constraints, lst_length)):
            constraints = randomly_select_constraints(all_possibilities, num_main_constraints)

        constraints = insert_duplicates(constraints, num_dup_constraints)

        assert(len(constraints) == NUM_CONSTRAINTS)
        filename = "input" + str(lst_length) + ".in"
        utils.output_to_file(names, constraints, filename)
        check([filename, lst_length]) # Checks each input file in correct form according to spec.

    print("All output files written!")

if __name__ == "__main__":
    main()