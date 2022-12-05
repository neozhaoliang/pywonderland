"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Run coset enumeration examples using Todd-Coxeter algorithm
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This script reads information of a finitely presented group
from a .yaml file and computes its coset table.

Example usage:

    python example_run_coset_enumeration.py filename [-std] [-o output]

    filename: required, the .yaml file to be parsed.
        -std: optional, if added then the output table is standard.
          -o: optional, output filename, the default is sys.stdout.

:copyright (c) 2018 by Zhao Liang.
"""
import argparse
import re
import sys
import yaml

from polytopes.todd_coxeter import CosetTable


def get_symbols(wordslist):
    """Collect the set of letters from a list of strings.
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
    """
    Find the integer in the generator list that represents a symbol `c`.
    """
    ind = symbols.index(c.lower())
    return 2 * ind if c.islower() else 2 * ind + 1


def word2int(symbols, wordslist):
    """
    Map a list of words to the list of their integer representations.
    """
    return tuple(tuple(char2int(symbols, c) for c in word) for word in wordslist)


def parse_latex(string):
    """
    Given a generator relation as a LaTeX string, convert it to a flattened string.
    Examples: a^{3} -> aaa, (ab)^2 -> abab, (aB)^{-2} -> bAbA
    """
    if len(string) == 0:
        return ""
    if "^" not in string:
        return string

    pattern = "(?:[a-zA-Z]{1}|\([a-zA-Z]+\))\^(?:\d+|\{-?\d+\})|[a-zA-Z]+(?!\^)"
    result = re.findall(pattern, string)
    word = ""
    for substring in result:
        if "^" not in substring:
            word += substring
        else:
            base, exponent = substring.split("^")
            if base[0] == "(":
                base = base[1:-1]
            if exponent[0] == "{":
                exponent = exponent[1:-1]

            exponent = int(exponent)
            if exponent < 0:
                exponent = -exponent
                base = base[::-1].swapcase()

            word += base * exponent

    return word

class FpGroup(object):

    """
    Finitely presented group by defining relations between its generators.
    """

    def __init__(self, relators, subgens=None, name=None):
        """
        :param relators: relations between the generators as a 1D list
            of strings, e.g. ["aaa", "bb", "abab"].

        :param subgens:  generators of the subgroup as a 1D list of
            strings, e.g. ["ab", "Ab"]

        :param name: decriptive name of the group, e.g. "S3", "D8", ..., etc.
        """
        if not name:
            name = self.__class__.__name__
        self.name = name
        self.relators = [parse_latex(s) for s in relators]
        self.generators = get_symbols(self.relators)
        if len(self.generators) < 2:
            raise ValueError("Not enough generators")
        if not subgens:
            subgens = []
        else:
            subgens = [parse_latex(s) for s in subgens]
        self.subgens = subgens

        # initialize the coset table
        gens = tuple(range(2 * len(self.generators)))
        relators += tuple(c + c.upper() for c in self.generators)
        rels = word2int(self.generators, self.relators)
        subgens = word2int(self.generators, self.subgens)
        self.coset_table = CosetTable(gens, rels, subgens, coxeter=False)

    def __str__(self):
        s = "\nName: {}\n".format(self.name)
        s += "Generators: " + ", ".join(self.generators)
        s += "\nRelators: " + ", ".join(self.relators)
        s += "\nSubgroup generators: " + ", ".join(self.subgens)
        return s

    def compute(self, standard=True):
        self.coset_table.run(standard)

    def print_table(self, outfile):
        """pretty print the table.
        """
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
    parser.add_argument(
        "-std", type=bool, default=True, help="Standardize the coset table or not"
    )
    parser.add_argument(
        "-out", metavar="-o", type=str, default=None, help="output file name"
    )
    args = parser.parse_args()

    with open(args.filename, "r") as f:
        data = yaml.safe_load(f)
        rels = data["relators"]
        subg = data["subgroup-generators"]
        name = data["name"]
        G = FpGroup(rels, subg, name)
        G.compute(args.std)
        G.print_table(args.out)


if __name__ == "__main__":
    main()
