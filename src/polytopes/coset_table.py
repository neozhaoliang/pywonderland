# -*- coding: utf-8 -*-
"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Coset Enumeration using Todd-Coxeter Algorithm
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Reference:
    [1] "Handbook of Computational Group Theory", Holt, D., Eick, B., O'Brien, E.
    [2] "Computation with finitely presented groups", Charles C.Sims.
    [3] GAP doc at "https://www.gap-system.org/Manuals/doc/ref/chap47.html".
    [4] Ken Brown's code at "http://www.math.cornell.edu/~kbrown/toddcox/".
"""
from tqdm import tqdm, trange


def inv(x):
    """Switch between a generator and its inverse."""
    return x + 1 if x % 2 == 0 else x - 1


class CosetTable(object):
    """
    Let G = < X | R > be a finitely presented group and H be a subgroup of G with
    |G:H| < inf. The coset table `T` of G/H is a 2D array with rows indexed by the
    right cosets of G/H and columns indexed by the generators of G and their inverses.
    The entry of T at row k and column x (x is a generator of the inverse of a generator)
    records the right action of coset k by x: T[k][x] = kx. If T[k][x] is not defined
    yet we set it to `None`. When the algorithm terminates all entries in the table are
    assigned a non-negative integer, all rows scan correctly under all words in R,
    and the 0-th row scan correctly under all generators of H.
    
    Example: G = <a, b | a^2 = b^3 = (ab)^3 = 1>, H = <ab>, and 
              a  A  b  B
          -------------
          0:  1  1  2  1
    T  =  1:  0  0  0  2
          2:  3  3  1  0
          3:  2  2  3  3
    
    where aA = Aa = 1, bB = Bb = 1.  
    """
    def __init__(self, gens, rels, subgens):
        """
        gens: a 1D list of integers that represents the generators,
              e.g. [0, 1, 2, 3] for [a, A, b, B]
        rels: a 2D list of integers that represents the relators R,
              e.g. [[0, 0], [2, 2, 2], [0, 2]*3] for a^2 = b^3 = (ab)^3 = 1
        subgens: a 2D list of integers that represents the subgroup generators,
              e.g. [[0, 2]] for <ab>.
              
        we use a list `p` to hold the equivalence classes of the cosets,
        p[k] = l means k and l really represent the same coset. It's always
        true that p[k] <= k, if p[k] = k then we call k "alive" else we call k "dead".
        All cosets are created "alive" but as the algorithm runs some of them may be
        declared to "dead" and their rows are deleted from the table (we do not explicitly
        free the memory of these row but keep in mind that they do not belong to our table).
        
        A "dead" coset arise when an `coincidence` is found, and while handling this
        coincidence more coincidences may also be found, so we use a queue `q` to hold them.
        """
        self.A = gens     # generators of G
        self.R = rels     # relations R between the generators
        self.H = subgens  # generators of H
        self.p = [0]      # initially we only have the 0-th coset `H`
        self.q = []       # a queue holds all dead cosets to be processed.
        self.table = [[None] * len(self.A)]
        self.bar = tqdm(desc="Defining new cosets", unit=" cosets")
        self.bar.update(1)
        
    def __getitem__(self, item):
        return self.table.__getitem__(item)

    def __len__(self):
        return len(self.table)

    def is_alive(self, coset):
        """Check if a coset is alive."""
        return self.p[coset] == coset

    def is_defined(self, coset, x):
        """Check an entry is defined."""
        return self[coset][x] is not None

    def undefine(self, coset, x):
        self[coset][x] = None
        
    def define(self, coset, x):
        """
        To define a new coset we need to:
        1. Append a new empty row to the table.
        2. Fill the two entries.
        3. Add this new coset to `p`.
        """
        n = len(self.table)
        self.table.append([None] * len(self.A))
        self[coset][x] = n
        self[n][inv(x)] = coset
        self.p.append(n)
        self.bar.update(1)

    def rep(self, coset):
        """
        Find the minimal equivalent representative of a given coset and
        modify `p` along the way.
        """
        m = coset
        while m != self.p[m]:
            m = self.p[m]
        
        l = coset
        while l != self.p[l]:
            l, self.p[l] = self.p[l], m
        
        return m

    def merge(self, coset1, coset2):
        """
        Merge two equivalent cosets. The larger one is declared to "dead" and
        is added to the queue `q` to be process later on.
        """
        s = self.rep(coset1)
        t = self.rep(coset2)
        if s != t:
            s, t = min(s, t), max(s, t)
            self.p[t] = s
            self.q.append(t)
        
    def scan_and_fill(self, coset, word):
        """
        Scan the row of a coset under a given word.
        1. Firstly we start from the left and scan forward to the right as far as possible.
           (1a) If it completes correctly then it yields no information, return.
           (1b) If it completes incorrectly then a coincidence is found, process it.
           (1c) If it does not complete, go to step 2.
        2. Then we start from the right and scan backward to the left as far as possible until
           it "meets" the forward scan `f`. Let this scan results in coset `b`.
           (2a) if `f` and `b` overlap, then a coincidence is found, process it.
           (2b) if `f` and `b` are about to meet (with a length 1 gap between) then a deduction
                is found, fill in the two new entries.
           (2c) else the scan is incomplete, define a new coset and continue scanning forward.
        """
        f = coset
        b = coset
        i = 0
        j = len(word) - 1
        while True:
            # scan forward as far as possible.
            while i <= j and self.is_defined(f, word[i]):
                f = self[f][word[i]]
                i += 1
            # if complete
            if i > j:
                # if complete incorrectly a coincidence is found, process it.
                if f != b:
                    self.coincidence(f, b)
                # else the scan yields no information
                return
            
            # if scan forward is not completed then scan backward as far as possible.
            # until it meets the forward scan.
            while j >= i and self.is_defined(b, inv(word[j])):
                b = self[b][inv(word[j])]
                j -= 1
            
            # if f and b overlap then a coincidence is found.
            if j < i:
                self.coincidence(f, b)
                return
            # if f and b are about to meet a deduction is found.
            elif j == i:
                self[f][word[i]] = b
                self[b][inv(word[i])] = f
                return
            # else they do not meet, define a new coset and continue scanning forward.
            else:
                self.define(f, word[i])
    
    def coincidence(self, coset1, coset2):
        """
        Process a coincidence. When two cosets are found to be equivalent the larger one
        is deleted: we need to copy all information in its row to the equivalent row and
        modify all entries it occurs in the table. During this process new coincidences
        may be found and they are also processed. The subtle thing here is that we must keep
        filling/deleting entries in pairs, i.e. we must make sure the table always satisfy
        table[k][x] = l <===> table[l][y] = k (y = inv(x)).
        """
        self.merge(coset1, coset2)
        # at this stage the queue contains only one item,
        # but new items may be added to it later.
        while len(self.q) > 0:
            e = self.q.pop(0)
            for x in self.A:
                if self.is_defined(e, x):
                    f = self[e][x]
                    y = inv(x)
                    # the entry (f, y) in the row f is also deleted since we must
                    # make sure all entries in the table come in pairs.
                    self.undefine(f, y)
                    # copy the information at (e, x) to (e1, x),
                    # but is (e1, x) already defined?
                    e1 = self.rep(e)
                    f1 = self.rep(f)
                    # if (e1, x) is already defined, a new coincidence is found.
                    if self.is_defined(e1, x):
                        self.merge(f1, self.table[e1][x])
                    elif self.is_defined(f1, y):
                        self.merge(e1, self.table[f1][y])
                    else:
                        # else (e1, x) is not defined, copy the information at (e, x) to (e1, x).
                        self[e1][x] = f1
                        self[f1][y] = e1
                        # keep in mind all changes come in pairs,
                        # so we also copy the information at (f, y) to (f1, y).

    def hlt(self):
        """
        Run the HLT strategy (Haselgrove, Leech and Trotter).
        """
        for word in self.H:
            self.scan_and_fill(0, word)
            
        current = 0
        while current < len(self.table):
            for rel in self.R:
                if not self.is_alive(current):
                    break
                self.scan_and_fill(current, rel)
 
            if self.is_alive(current):
                for x in self.A:
                    if not self.is_defined(current, x):
                        self.define(current, x)
            current += 1

        self.bar.close()
            
    def compress(self):
        """
        Delete all dead cosets in the table.
        The live cosets are renumbered and their entries are also updated.
        """
        ind = -1
        for coset in trange(len(self), desc="Compressing the table"):
            if self.is_alive(coset):
                ind += 1
                if ind != coset:
                    for x in self.A:
                        y = self[coset][x]
                        if y == coset:
                            self[ind][x] = ind
                        else:
                            self[ind][x] = y
                            self[y][inv(x)] = ind

        self.p = list(range(ind + 1))
        self.table = self.table[:len(self.p)]       
            
    def swap(self, k, l):
        """
        Swap two *live* cosets in the table. It's called in the `standardize()` method
        after the table is compressed, but it also works for non-compressed table. 
        """
        for x in self.A:
            # swap the two rows k and l.
            self[k][x], self[l][x] = self[l][x], self[k][x]
            # modify all k/l in the table.
            for coset in range(len(self)):
                # this check is not required for a compressed table.
                if self.is_alive(coset):
                    if self[coset][x] == k:
                        self[coset][x] = l
                    elif self[coset][x] == l:
                        self[coset][x] = k
        
    def standardize(self):
        """
        Rearrange the cosets in the table to a standard form.
        """
        # the next coset we want to encounter in the table.
        next_coset = 1
        for coset in trange(len(self), desc="Standardizing the table"):
            for x in self.A:
                y = self[coset][x]
                if y >= next_coset:
                    if y > next_coset:
                        self.swap(y, next_coset)
                    next_coset += 1
                    if next_coset == len(self) - 1:
                        return
