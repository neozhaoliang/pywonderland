"""
Sample a random state in a finite, irreducible Markov chain from its
stationary distribution using monotone CFTP.
"""
import random
from tqdm import tqdm


class MonotoneMarkovChain:

    """
    This class holds a Markov chain object that implements following methods:

    1. `new_random_update`: return a new random updating operation.
    2. `update`: update a state by an updating operation.
    3. `min_max_states`: return the minimum and maximum states.
    """

    def min_max_states(self):
        raise NotImplementedError

    def new_random_update(self):
        raise NotImplementedError

    def update(self, state, operation):
        raise NotImplementedError

    def run(self):
        bar = tqdm(desc="Running cftp", unit=" steps")
        updates = [(random.getstate(), 1)]
        while True:
            # run two versions of the chain starting from the min/max
            # states in each round
            s0, s1 = self.min_max_states()
            rng_next = None
            for rng, steps in updates:
                random.setstate(rng)
                for _ in range(steps):
                    u = self.new_random_update()
                    self.update(s0, u)
                    self.update(s1, u)
                    bar.update(1)

                # save the latest random seed for future use.
                if rng_next is None:
                    rng_next = random.getstate()

            # check if these two chains are coupled at time 0.
            if s0 == s1:
                break

            # if not coupled then look further back into the past.
            updates.insert(0, (rng_next, 2 ** len(updates)))

        random.setstate(rng_next)
        bar.close()
        # you can return either s0 or s1 here since they are coupled together
        return s0
