"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Word processing in Coxeter groups
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

With this class you can:

1. Build and visualize the automaton that recognizes the shortlex language of a Coxeter group.
2. Compute the normal form of a word (hence also the multiplication of two words).
3. Compute the set of minimal representatives of a standard parabolic subgroup.
4. Compute the coset table for a standard parabolic subgroup. For infinite Coxeter groups
   (i.e. affine and hyperbolic groups) the table is generated up to a given depth.

Important: always be aware of left and right cosets when computing coset representatives, in this
program we use the left convention: x for xH (assuming x = s₁s₂...sₙ is a shortlex word).
"""
from collections import deque
from itertools import combinations
import numpy as np

from .integer import lcm
from .polynomial import IntPolynomial
from .algebraic import AlgebraicInteger
from .root import Root
from .automata import DFA, DFAState


class CoxeterGroup(object):

    """
    Attributes:

    cox_mat : Coxeter matrix of this group.

    rank : rank of this Coxeter group, i.e. number of generators.

    reftable : reflection table of the minimal roots. This is a 2d array whose rows are
        indexed by the minimal roots and columns are indexed by the simple reflections.

    dfa : the minimal automaton that recognizes the shortlex language of this group.

    m : order of the primitive root of unity that generates the cyclotomic field.

    phix : the cyclotomic polynomial for the cyclotomic field that all entries of the
        Cartan matrix lie in. Its degree equals φ(m) where φ is Euler's totient function.

    cartan_mat : Cartan matrix of this Coxeter group. Its entries are all algebraic integers
        in the m-th cyclotomic field.
    """

    def __init__(self, cox_mat):
        """
        A Coxeter group is initialized by a Coxeter matrix.

        Example:
        >>> cox_mat = [[1, 3, 3], [3, 1, 3], [3, 3, 1]]
        >>> G = CoxeterGroup(cox_mat)

        If there are infinities in the Coxeter matrix, simply replace them with -1.

        Example:
        >>> cox_mat = [[1, -1], [-1, 1]]
        >>> G = CoxeterGroup(cox_mat)
        """
        self.cox_mat = np.array(cox_mat, dtype=np.int)
        self.check_coxeter_matrix(self.cox_mat)

        self.rank = len(cox_mat)
        self.gens = tuple(range(self.rank))
        self.m, self.phix = self.get_cyclotomic_field()
        self.cartan_mat = None  # cartan matrix
        self.reftable = None  # reflection table of minimal roots
        self.dfa = None  # automaton for shortlex language
        self.minroots = None  # minimal roots

    def init(self):
        """
        Delegate the computations of the Cartan matrix, reflection table of minimal roots
        and the automaton to this method.
        """
        self.get_cartan_matrix()
        self.get_reflection_table()
        self.get_automaton()
        return self

    @staticmethod
    def check_coxeter_matrix(M):
        if not ((M == M.T).all() and (np.diag(M) == 1).all()):
            raise ValueError("Invalid Coxeter matrix: {}".format(M))

    def get_cyclotomic_field(self):
        m = 2
        for k in 2 * self.cox_mat.ravel():
            m = lcm(m, k)
        p = IntPolynomial.cyclotomic(m)
        return (m, p)

    def get_latex_presentation(self):
        """
        Return a presentation of this group in latex format.
        """
        latex = r"$$\langle {} \, |\, {}={}=1\rangle.$$"
        gens = ",".join("s_{{{}}}".format(i) for i in self.gens)
        invs = "=".join("s^2_{{{}}}".format(i) for i in self.gens)
        rels = "=".join("(s_{{{}}}s_{{{}}})^{}".format(i, j, self.cox_mat[i][j])
                        for i, j in combinations(self.gens, 2))
        return latex.format(gens, invs, rels)

    @staticmethod
    def get_latex_words_array(words, symbol=r"s", cols=4):
        """
        Convert a list of words to latex format.

        :param cols: number of columns of the output latex array.
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
        """
        Traverse the automaton and yield the coset representatives of a given standard
        parabolic subgroup along the way up to a given depth. If depth is None then it
        will try to traverse up to a maximum number of words.

        :param depth: search for words up to this length.

        :param maxcount: upper bound for the number of words.

        :param parabolic: generators of the standard parabolic subgroup.

        :param right: A bool type for choosing right or left coset representatives.

        Example
        >>> parabolic=(1, 2)  # standard parabolic subgroup H = <s₁, s₂>
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

    def _left_mult_invshortlex(self, s, word):
        """
        :param s: a generator represented by an integer.

        :param word: a word represented by a tuple of integers. This word must be in the
            inverse shortlex normal form.

        Multiply an inverse shortlex word by a generator s on the left: w --> sw.
        The result is also a reduced inverse shortlex word. For more details about
        the algorithm see:

               https://www.math.ubc.ca/~cass/research/pdf/roots.pdf

        Example:
        >>> cox_mat = [[1, 3, 3], [3, 1, 3], [3, 3, 1]]
        >>> G = CoxeterGroup(cox_mat)
        >>> s = 1  # generator s₁
        >>> word = (0, 2, 1, 0)  # s₀s₂s₁s₀ is an invserse shortlex word
        >>> G._left_mult_invshortlex(s, word)  # compute s₁s₀s₂s₁s₀
        >>> (1, 0, 2, 1, 0)  # the result s₁s₀s₂s₁s₀ is also an inverse shortlex word
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
        """
        :param s: a generator represented by an integer.

        :param word: a word represented by a tuple of integers. This word must be in the
            shortlex normal form.

        Multipy a shortlex word by a generator s on the right: w --> ws. The result is also
        a reduced shortlex word. We simply make it an inverse shortlex word first by reversing
        it, then multiply s on the left and finally reverse it back.
        """
        word = reversed(word)
        return self._left_mult_invshortlex(s, word)[::-1]

    def multiply(self, s, word, right=True):
        """
        Multiply a shortlex word by a generator s on the left or right. The result is also
        a reduced word in shortlex order. If multiply on the left then we progressively
        compute sw = s(s₁s₂...sₙ) = (ss₁)s₂...sₙ = ((ss₁)s₂))...sₙ by multiplying each sᵢ
        on the right.
        """
        if right:
            return self._right_mult_shortlex(s, word)
        else:
            result = (s,)
            for s_i in word:
                result = self._right_mult_shortlex(s_i, result)
            return result

    def reduce(self, word):
        """
        Reduce a word to its shortlex normal form. This method is also used for multiplying
        two words w₁ and w₂, simply apply 'reduce' to (w₁ + w₂).
        """
        result = ()
        for s_i in word:
            result = self.multiply(s_i, result, right=True)
        return result

    def is_reduced(self, word):
        """
        Check if a word is a reduced shortlex word.
        """
        return self.reduce(word) == word

    def get_coset_representative(self, word, parabolic=(), right=False):
        """
        :param word: a given word represented by a tuple of integers.

        :param parabolic: generators of the standard parabolic subgroup.

        :param right: choose to return representative of the left/right coset.

        Get the minimal (left or right) coset representative in the coset wH where w is a
        given word and H is a standard parabolic subgroup.
        """
        if len(word) == 0:
            return tuple()

        while True:
            w = word
            for s in parabolic:
                # right coset requires multiply subgroup generator s on the left,
                # left coset requires multiply subgroup generator s on the right.
                sw = self.multiply(s, w, right=not right)
                if len(sw) < len(w):
                    w = sw
            if len(w) == len(word):
                break
            word = w
        return word

    @staticmethod
    def sort_words(words):
        """
        Sort a list of words by shortlex order.
        """
        return tuple(sorted(words, key=lambda x: (len(x), x)))

    def get_coset_table(self, words, parabolic=()):
        """
        Return the coset table T for a given list of representatives of the left cosets
        of a standard parabolic subgroup. Here the rows of T are index by the coset
        representatives and the columns are indexed by the generators of the group.
        T[i][j] is the word obtained by multiplying the j-th generator on the left of
        the i-th word. If the resulting word is not in the list then the entry is set
        to None. The representatives are assumed to be in normal form of shortlex order.
        """
        T = [[None] * self.rank for _ in range(len(words))]
        for i, word in enumerate(words):
            for j in self.gens:
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

    def move(self, coset_table, v, word):
        """
        :param coset_table: a coset table.
        :param v: a coset represented by an integer.
        :param word: a tuple of integers.

        Return the the coset by applying 'word' to 'v'.
        """
        for w in reversed(word):
            v = coset_table[v][w]
            if v is None:
                return None
        return v

    def get_cartan_matrix(self):
        """
        Get the Cartan matrix with entries -2*cos(π / m[i][j]).
        """
        M = self.cox_mat
        n = self.rank
        m = self.m
        p = self.phix
        C = np.zeros_like(M).astype(object)

        # diagonal entries
        np.fill_diagonal(C, AlgebraicInteger(p, 2))

        # non-diagonal entries
        for i in range(n):
            for j in range(i):
                z = [0] * m
                k = 2 * M[i][j]
                if k > 0:
                    z[m // k] = -1
                    z[m - m // k] = -1
                    zeta = AlgebraicInteger(p, IntPolynomial(z))
                    C[i][j] = C[j][i] = zeta
                else:
                    C[i][j] = C[j][i] = AlgebraicInteger(p, -2)

        self.cartan_mat = C

    def get_simple_reflection(self, k):
        """
        Return the reflection matrix for the k-th simple root.
        """
        S = np.eye(self.rank, dtype=object)
        S[k] -= self.cartan_mat[k]
        return S

    def get_reflection_table(self):
        """
        Get the reflection table of the minimal roots.
        For example the triangle group (3, 4, 3):

        >>> cox_mat = [[1, 3, 4], [3, 1, 3], [4, 3, 1]]
        >>> G = CoxeterGroup(cox_mat)
        >>> G.init()
        >>> G.reftable
        >>> array([[-1, 3, 4],
                   [3, -1, 5],
                   [6, 5, -1],
                   [1, 0, None],
                   [4, None, 0],
                   [None, 2, 1],
                   [2, None, 6]], dtype=object)

        Let αᵢ be the i-th minimal root and sⱼ be the j-th simple reflection, then
        1. reftable[i][j] = -1 if and only if sⱼ(αᵢ) is a negative root. This happens
           only when αᵢ is also a simple root and i = j.
        2. reftable[i][j] = None if and only if sⱼ(αᵢ) is a positive root but not minimal.
        3. reftable[i][j] = k (k >= 0) if and only if sⱼ(αᵢ) is the k-th minimal root.
        So there are 7 minimal roots for the group (3, 4, 3).
        """
        M = self.cox_mat
        n = self.rank
        p = self.phix
        I_n = np.eye(n, dtype=int)

        # matrices of the simple reflections
        R = [self.get_simple_reflection(k) for k in range(n)]
        max_order = np.amax(M)
        # a tricky way to store the set of m_ij's in the Coxeter matrix
        mset = 0
        for k in M.ravel():
            if k > 2:
                mset |= (1 << k)

        # a root is in the queue if and only if its coords are known but its reflections are not.
        queue = deque()
        # a root is appended to the list only after all its information are known
        roots = []
        count = 0  # current number of minimal roots
        MINUS = Root(index=-1)  # the negative root

        # generate all simple roots
        for i in range(n):
            coords = [AlgebraicInteger(p, 0) if k != i else AlgebraicInteger(p, 1) for k in range(n)]
            s = Root(coords=coords, index=count, mat=R[i])
            s.reflections = [None if k != i else MINUS for k in range(n)]
            queue.append(s)
            roots.append(s)
            count += 1

        # search from the bottom of the root graph to find all other minimal roots of depth >= 2
        while queue:
            alpha = queue.popleft()
            for i in range(n):
                if alpha.reflections[i] is None:
                    beta = Root(coords=np.dot(R[i], alpha.coords))

                    # if beta is already a known minimal root.
                    # Note the trap here: don't use "if beta in roots:" !
                    for r in roots:
                        if beta == r:
                            alpha.reflections[i] = r
                            r.reflections[i] = alpha
                            break

                    else:
                        # beta is a new root, is it minimal?
                        # it's is minimal iff its reflection and s_i generate a finite group
                        is_minroot = False
                        S = np.dot(alpha.mat, R[i])
                        X = S
                        for j in range(2, max_order + 1):
                            X = np.dot(S, X)
                            # check if X^{m_{ij}} is the identity matrix
                            if ((1 << j) & mset != 0) and (X == I_n).all():
                                is_minroot = True
                                break

                        # beta is minimal
                        if is_minroot:
                            alpha.reflections[i] = beta
                            beta.reflections[i] = alpha
                            beta.mat = np.dot(R[i], S)
                            beta.index = count
                            count += 1
                            queue.append(beta)
                            roots.append(beta)

        # finally put all reflection information into a 2d array
        table = np.zeros((len(roots), n), dtype=object)
        for alpha in roots:
            k = alpha.index
            for i, beta in enumerate(alpha.reflections):
                symbol = beta.index if beta is not None else None
                table[k][i] = symbol

        self.roots = roots
        self.reftable = table

    def get_automaton(self, type="shortlex"):
        """
        Construct the automaton that recognizes the language of a Coxeter group.
        """
        if type not in ["shortlex", "reduced"]:
            raise ValueError("Unknown type of automaton, must be 'reduced' or 'shortlex'")

        table = self.reftable
        n = self.rank

        def subset_transition(S, i):
            """
            S is a subset of the set of minimal roots, this function computes the transition
            of S by the simple reflection sᵢ in the automaton. The transition rule for the
            automaton of "reduced words" is: for sᵢ ∉ S,
                   sᵢ
                S -----> {sᵢ} ∪ (sᵢ(S) ∩ Σ)
            where Σ is the set of minimal roots.
            For the automaton of "shortlex normal forms" the transition rule is
                   sᵢ
                S -----> {sᵢ} ∪ (sᵢ(S) ∪ {sᵢ(αⱼ), j<i}) ∩ Σ
            """
            if i in S:
                return None

            result = set([i])
            for j in S:
                k = table[j][i]
                if k is not None:
                    result.add(k)

            if type == "shortlex":
                for j in range(i):
                    k = table[j][i]
                    if k is not None:
                        result.add(k)

            return frozenset(result)

        start = DFAState(frozenset())
        queue = deque([start])
        states = [start]

        # this is just a breadth-first search of the automaton.
        while queue:
            S = queue.popleft()
            for i in self.gens:
                # if the transition of S by i is unknown
                if i not in S.transitions:
                    # compute the transition
                    t = subset_transition(S.subset, i)
                    if t is not None:
                        # so t is a subset in the automaton, have we seen it yet?
                        found = False
                        for T in states:
                            # we have seen t before, simply add the transition
                            if t == T.subset:
                                S.add_transition(i, T)
                                found = True
                                break

                        if not found:
                            # t is a new subset, create a new state for it.
                            T = DFAState(t)
                            S.add_transition(i, T)
                            queue.append(T)
                            states.append(T)
        # get the minimized dfa
        self.dfa = DFA(start, self.gens).minimize()
