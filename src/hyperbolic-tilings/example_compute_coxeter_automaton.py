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
from coxeter import get_automaton


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", help="Coxeter matrix data file")
    args = parser.parse_args()
    cox_mat = np.loadtxt(args.filename, dtype=np.int, delimiter=" ")
    print("Computing the shorlex DFA for Coxeter group:")
    print(cox_mat)
    dfa = get_automaton(cox_mat, type="shortlex")
    print("The minimal DFA contains {} states".format(dfa.num_states))
    imgname = os.path.splitext(os.path.basename(args.filename))[0] + ".png"
    dfa.draw(imgname)


if __name__ == "__main__":
    main()
