# -*- coding: utf-8 -*-
"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Compute the automaton that recognizes the language of a Coxeter group
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
from collections import deque
import pygraphviz
from minroots import get_reflection_table


class DFAState(object):

    def __init__(self, subset, accept=True):
        """`subset`: a subset of the set of minimal roots, stored in a frozenset.
        """
        self.subset = subset
        self.accept = accept
        self.index = None
        self.transitions = dict()

    def __str__(self):
        return str(self.subset)

    __repr__ = __str__

    def add_transition(self, symbol, target):
        if symbol in self.transitions:
            raise ValueError("state already has this transition")
        self.transitions[symbol] = target

    def all_transitions(self):
        return self.transitions.items()

    def draw(self, G, found, color="black"):
        if self in found:
            return
        found.add(self)
        shape = "doublecircle" if self.accept else "circle"
        G.add_node(self.index, shape=shape, color=color)
        for symbol, target in self.all_transitions():
            target.draw(G, found)
            G.add_edge(self.index, target.index, label=symbol)


class DFA(object):

    def __init__(self, start):
        self.start = start
        self.num_states = self.reindex(self.start, 0)

    def reindex(self, state, next_index):
        """Reindex the states in the automaton.
        """
        if state.index is None:
            state.index = next_index
            next_index += 1
            for _, target in state.all_transitions():
                next_index = self.reindex(target, next_index)
        return next_index

    def draw(self, filename, program="dot"):
        """Use graphviz to draw this automaton.
        """
        G = pygraphviz.AGraph(strict=False, directed=True, rankdir="LR")
        self.start.draw(G, set(), color="red")
        G.draw(filename, prog=program)
        return self


def build_automaton(cox_mat):
    """build the automaton that recognizes the language of a Coxeter group.
    """
    rank = len(cox_mat)
    table = get_reflection_table(cox_mat)

    def subset_transition(S, i):
        """`S` is a subset of the set of minimal roots, this function computes
           the transition of S by the simple reflection s_i in the automaton.
        """
        if i in S:
            return None
        result = set([i])
        for j in S:
            k = table[j][i]
            if k is not None:
                result.add(k)
        return frozenset(result)

    start = DFAState(frozenset())
    queue = deque([start])
    states = [start]

    while queue:
        S = queue.popleft()
        for i in range(rank):
            if i not in S.transitions:
                t = subset_transition(S.subset, i)
                if t is not None:
                    found = False
                    for T in states:
                        if t == T.subset:
                            S.add_transition(i, T)
                            found = True
                            break
                    if not found:
                        T = DFAState(t)
                        S.add_transition(i, T)
                        queue.append(T)
                        states.append(T)

    return DFA(start)


def test():
    cox_mat = [[1, 3, 3], [3, 1, 3], [3, 3, 1]] # affine A_2 Coxeter group
    dfa = build_automaton(cox_mat)
    print("The automaton contains {} states".format(dfa.num_states))
    dfa.draw("a2~.png")


if __name__ == "__main__":
    test()
