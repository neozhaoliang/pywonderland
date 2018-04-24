# -*- coding: utf-8 -*_
"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This script reads information of a group from
a .yaml file and computes its coset table.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Example usage:

    python run_coset_enum.py filename [-std] [-o][filename]

    filename: required, the .yaml file to be parsed.
        -std: optional, needs no value, if added then
              the output table is standardized.
          -o: optional, output filename, the default
              one is sys.stdout.
"""
import sys
import argparse
import yaml
from todd_coxeter import CosetTable


def get_symbols(wordslist):
    """
    Collect the set of letters from a list of strings.
    """
    symbols = []
    for word in wordslist:
        for x in word:
            x = x.lower()
            if not x.isalpha():
                raise ValueError("Only a-z and A-Z are allowed.")
            if x not in symbols:
                symbols.append(x)
    return sorted(symbols)


def char2int(symbols, c):
    ind = symbols.index(c.lower())
    return 2 * ind if c.islower() else 2 * ind + 1


def word2int(symbols, wordslist):
    return tuple(tuple(char2int(symbols, c) for c in word)
                 for word in wordslist)


class FpGroup(object):

    def __init__(self, relators, subgens=None, name=None):
        """
        relators: relations between the generators as a 1D list
                  of strings, e.g. ["aaa", "bb", "abab"].
        subgens:  generators of the subgroup as a 1D list of
                  strings, e.g. ["ab", "Ab"]
        name: decriptive name of the group, e.g. "S3", "D8", ..., etc.
        """
        if not name:
            name = self.__class__.__name__
        self.name = name
        self.relators = relators
        self.generators = get_symbols(relators)
        if len(self.generators) < 2:
            raise ValueError("Not enough generators")
        if not subgens:
            subgens = []
        self.subgens = subgens

        # initialize the coset table
        gens = tuple(range(2 * len(self.generators)))
        relators += tuple(c + c.upper() for c in self.generators)
        rels = word2int(self.generators, relators)
        subgens = word2int(self.generators, self.subgens)
        self.coset_table = CosetTable(gens, rels, subgens)

    def __str__(self):
        s = "\nName: {}\n".format(self.name)
        s += "Generators: " + ", ".join(self.generators)
        s += "\nRelators: " + ", ".join(self.relators)
        s += "\nSubgroup generators: " + ", ".join(self.subgens)
        return s

    def compute(self, standard=True):
        self.coset_table.run(standard)

    def print_table(self, outfile):
        f = sys.stdout if outfile is None else open(outfile, "w")
        f.write("       ")
        for x in self.generators:
            f.write("{:>5s}".format(x))
            f.write("{:>5s}".format(x.upper()))
        f.write("\n" + (2 * len(self.generators) + 2) * 5 * "-" + "\n")

        for i, row in enumerate(self.coset_table, start=1):
            f.write("{:>5d}: ".format(i))
            for x in row:
                f.write("{:>5d}".format(x + 1))
            f.write("\n")
        f.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", type=str, help="Input file name")
    parser.add_argument("-std", type=bool, default=True,
                        help="Standardize the coset table or not")
    parser.add_argument("-out", metavar="-o", type=str,
                        default=None, help="output file name")
    args = parser.parse_args()
    with open(args.filename, "r") as f:
        data = yaml.load(f)
        rels = data["relators"]
        subg = data["subgroup-generators"]
        name = data["name"]
        G = FpGroup(rels, subg, name)
        G.compute(args.std)
        G.print_table(args.out)


if __name__ == "__main__":
    main()
