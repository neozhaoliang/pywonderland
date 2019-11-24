"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Load Coxeter matrix from a txt file and compute its DFA
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Example usage:

    python example_compute_coxeter_automaton.py cox_examples/343.txt

warning: for a large DFA it may take quite long time for graphviz to draw the image.
"""
import os
import argparse
import numpy as np
from coxeter import CoxeterGroup


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", help="Coxeter matrix data file")
    args = parser.parse_args()
    cox_mat = np.loadtxt(args.filename, dtype=np.int, delimiter=" ")
    print("Computing the shorlex DFA for Coxeter group:")
    print(cox_mat)
    G = CoxeterGroup(cox_mat).init()
    print("The minimal DFA contains {} states".format(G.dfa.num_states))
    imgname = os.path.splitext(os.path.basename(args.filename))[0] + ".png"
    G.dfa.draw(imgname)


if __name__ == "__main__":
    main()
