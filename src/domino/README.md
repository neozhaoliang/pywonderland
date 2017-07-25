# Domino Shuffling Algorithm on Aztec Diamond Graphs.

## What is domino shuffling algorithm

Domino shuffling comes from combinatorics (a branch of mathematics). It firstly appeared as the fourth method in [a paper](https://arxiv.org/abs/math/9201305) proposed by Elkies, Kuperberg, Larsen and Propp to enumerate the number of domino tilings of aztec diamond graphs. In our project, it's used to sample a random tiling among all tilings with equal probability. Compare this with the Wilson algorithm animation in this repo, basically they are both devised to do the same thing: sample with uniform probability from a very very large set (in fact they can be generalized to sample under any given probability distribution). There are two reasons one should love it:

1. It's quite dedicate, just watch the gif animation in the front page. In fact until today it's still the most beautiful solution to the enumeration of domino tilings of aztec graphs.

2. It lies at the crossroad of combinatorics, probability theory, representation theory, and statistical mechanics. Many many beautiful theories are linked together and many intriguing things still need to be explained.

Well I think I should stop preaching here. If you want to learn more about this subject, besides the original paper above, Propp's paper [generalized domino shuffling](https://arxiv.org/abs/math/0111034) also serves as a good starting point.


## About the code

I haven't much to say about the code. One must understand the algorithm before he could read the code, so please turn to the papers first.


There are two files `aztec.py` and `aztec_matplotlib.py` in this directory. They do the same job (random sampling) but one uses `cairo` for drawing and the other uses `matplotlib`. `cairo` is much faster than `matplotlib` but `matplotlib` renders better and much smaller images. So I used `cairo` to generate GIF animations and `matplotlib` to draw perfectly random tilings.
