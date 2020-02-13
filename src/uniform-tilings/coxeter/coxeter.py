"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Word processing in Coxeter groups
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

With this class you can:

    1. Build and visualize the automaton that recognizes the
       shortlex language of a Coxeter group.
    2. Compute the normal form of a word (hence also multiplications
       of two words).
    3. Compute the set of minimal representatives of a standard
       parabolic subgroup.
    4. Compute the coset table for a standard parabolic subgroup.
       For an infinite Coxeter group the table is generated up
       to a given depth.

Important: always be aware of left and right cosets when doing coset
computations, in this program we use the left cosets convention:
x for xH (assume x = s1s2...sn is a shortlex word).
"""
from collections import deque
from itertools import combinations
import numpy as np
from .reftable import get_reflection_table
from .automata import get_automaton


class CoxeterGroup(object):

    def __init__(self, cox_mat):
        """A Coxeter group is determined by a Coxeter matrix.
        """
        self.cox_mat = np.array(cox_mat, dtype=np.int)
        self.rank = len(cox_mat)
        self.reftable = None  # reflection table of minimal roots
        self.dfa = None  # automaton for shortlex language

    def init(self):
        """Delegate the computations of the reflection table and
           the automaton to this method.
        """
        self.reftable = get_reflection_table(self.cox_mat)
        self.dfa = get_automaton(self.reftable)
        return self

    def get_latex_presentation(self):
        """Return a presentation of this group in latex format.
        """
        latex = r"$$\langle {} \, |\, {}={}=1\rangle.$$"
        generators = ",".join("s_{{{}}}".format(i) for i in range(self.rank))
        involutions = "=".join("s^2_{{{}}}".format(i) for i in range(self.rank))
        relations = "=".join("(s_{{{}}}s_{{{}}})^{}".format(i, j, self.cox_mat[i][j])
                              for i, j in combinations(range(self.rank), 2))
        return latex.format(generators, involutions, relations)

    @staticmethod
    def get_latex_words_array(words, symbol=r"s", cols=4):
        """Convert a list of words to latex format.
           `cols` is the number of columns of the output latex array.
        """
        def to_latex(word):
            if len(word) > 0:
                return "".join(symbol + "_{{{}}}".format(i) for i in word)
            return "e"

        latex = ""
        for i, word in enumerate(words):
            if i > 0 and i % cols == 0:
                latex += r"\\"
            latex += to_latex(word)
            if i % cols != cols - 1:
                latex += "&"

        return r"\begin{{array}}{{{}}}{}\end{{array}}".format("l" * cols, latex)

    def traverse(self, depth=None, maxcount=20000, parabolic=(), right=False):
        """Traverse the automaton and yield the words along the
           way up to a given depth. If depth is set to `None` then
           it will try to traverse up to a maximum number of words.
        """
        if self.dfa is None:
            self.init()

        count = 0
        Q = deque([((), 0, self.dfa.start)])
        while Q:
            word, steps, state = Q.popleft()
            yield self.get_coset_representative(word, parabolic, right)
            count += 1
            if count >= maxcount:
                break

            if depth is None or steps < depth:
                for symbol, target in state.all_transitions():
                    Q.append((word + (symbol,), steps + 1, target))

    # ---------------------------------------------------
    # multiplications of shortlex words in Coxeter groups
    # ---------------------------------------------------

    def _left_mult_invshortlex(self, s, word):
        """Multiply an inverse shortlex word by a generator s on the
           left: w --> sw. The result is also a reduced inverse shortlex word.

           For more details about the algorithm see:

               https://www.math.ubc.ca/~cass/research/pdf/roots.pdf

          Example:
          >>> cox_mat = [[1, 3, 3], [3, 1, 3], [3, 3, 1]]
          >>> G = CoxeterGroup(cox_mat)
          >>> s = 0
          >>> word = (1, 0, 1, 0)  # this is an invserse shortlex word
          >>> G._left_mult_invshortlex(s, word)
          >>> (1 ,0, 0)  # the result is also an inverse shortlex word
        """
        # again check if we already have the reflection table.
        # note doing multiplications does not use the automaton.
        if self.reftable is None:
            self.init()

        word = tuple(word)
        t = s  # t is the label of the last exchange site
        k = -1  # index of the last exchange site
        mu = s  # mu = (si...s1)α_s
        for i, s_i in enumerate(word):
            mu = self.reftable[mu][s_i]
            if mu is None:
                return word[:k+1] + (t,) + word[k+1:]
            elif mu < 0:
                return word[:i] + word[i+1:]
            elif mu < s_i:
                t = mu
                k = i
            else:
                continue
        return word[:k+1] + (t,) + word[k+1:]

    def _right_mult_shortlex(self, s, word):
        """Multipy a shortlex word by a generator s on the right: w --> ws.
           The result is also a reduced shortlex word.
           We simply make it an inverse shortlex word first by reversing
           it, then multiply s on the left and finally reverse it back.
        """
        word = reversed(word)
        return self._left_mult_invshortlex(s, word)[::-1]

    def multiply(self, s, word, right=True):
        """Multiply a shortlex word by a generator s on the left or right.
           The result is also a reduced word in shortlex order. If
           multiply on the left then we progressively compute

               sw = s(s1s2...sn) = (ss1)s2...sn = ((ss1)s2))...sn

           by multiplying each si on the right.
        """
        if right:
            return self._right_mult_shortlex(s, word)
        else:
            result = (s,)
            for s_i in word:
                result = self._right_mult_shortlex(s_i, result)
            return result

    def reduce(self, word):
        """Reduce a word to its shortlex normal form.
           This method is also used for multiplying two words w1 and w2:
           simply call `reduce(w1 + w2)`.
        """
        result = ()
        for s_i in word:
            result = self.multiply(s_i, result, right=True)
        return result

    # ---------------------------------------------------
    # coset representative computations of shortlex words
    # ---------------------------------------------------

    def get_coset_representative(self, word, parabolic=(), right=False):
        """Get the minimal (left or right) coset representative for
           a given word with respect to a standard parabolic subgroup.
           Use `right=True` for right coset representatives and `right=False`
           for left coset representatives.
        """
        if len(word) == 0:
            return tuple()

        while True:
            w = word
            for s in parabolic:
                # right coset requires multiply s on the left,
                # left coset requires multiply s on the right.
                sw = self.multiply(s, w, right=not right)
                if len(sw) < len(w):
                    w = sw
            if len(w) == len(word):
                break
            word = w
        return word

    @staticmethod
    def sort_words(words):
        """Sort a list of words by shortlex order.
        """
        return tuple(sorted(words, key=lambda x: (len(x), x)))

    def get_coset_table(self, words, parabolic=()):
        """Return the coset table T for a given list of representatives of
           the left cosets of a standard parabolic subgroup. Here the rows of
           T are index by the coset representatives and the columns are indexed
           by the generators of the group. T[i][j] is the word obtained by
           multiplying the j-th generator on the left of the i-th word.
           If the resulting word is not in the list then the entry is set
           to None. The representatives are assumed to be in normal form of
           shortlex order.
        """
        T = [[None for _ in range(self.rank)] for _ in range(len(words))]
        for i, word in enumerate(words):
            for j in range(self.rank):
                if T[i][j] is None:
                    next_word = self.multiply(j, word, right=False)
                    next_word = self.get_coset_representative(next_word, parabolic)
                    try:
                        ind = words.index(next_word)
                        T[i][j] = ind
                        T[ind][j] = i
                    except ValueError:
                        pass
        return T

    def move(self, T, v, word):
        """For a given coset table `T`, a coset `v` (represented by an integer)
           and a `word`, return the the coset by applying `word` to `v`.
        """
        for w in reversed(word):
            v = T[v][w]
            if v is None:
                return None
        return v
