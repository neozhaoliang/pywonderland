# An Implementation of the Domino Shuffling Algorithm on Aztec Diamond Graphs.


## How to use this program

1. To sample a random tiling of an order 200 az graph and output an image of size 1000x1000, run
	```
	$ python aztec.py -order 200 -size 1000
	```
    or simply

	```
	$ python aztec.py -o 200 -size 1000
	```
	This will output an image named "randomtiling.png" in current directory. You may also specify the name of the image by adding the `-f` option:
    ```
	$ python aztec.py -o 200 -size 1000 -f filename
    ```

2. To make gif animations of the domino shuffling algorithm, for example, create a gif image of size 400x400 which animates the first 40 steps of the algorithm, run

	```
	$ python anim.py -order 40 -size 400
	```

	or simply

	```
	$ python anim.py -o 40 -s 400
    ```


**Important Note: **  `anim.py` requires `ImageMagick` be installed on your computer. For windows users you also need to set the `CONVERTER` variable in `anim.py` to be the path to your `convert.exe`.


## What is domino shuffling algorithm

Domino shuffling comes from combinatorics (a branch of mathematics). It firstly appeared as the fourth method in [a paper](https://arxiv.org/abs/math/9201305) proposed by Elkies, Kuperberg, Larsen and Propp to enumerate the number of domino tilings of aztec diamond graphs. In our project, it's used to sample a random tiling among all tilings with equal probability. Compare this with the Wilson algorithm animation in this repo, basically they are both devised to do the same thing: sample with uniform probability from a very very large set (in fact they can be generalized to sample under any given probability distribution). There are two reasons one should love it:

1. It's quite dedicate. Just watch the gif animation in the front page. In fact until today it's still the most beautiful solution to the enumeration of domino tilings of aztec graphs.

2. It lies at the crossroad of combinatorics, probability theory, representation theory, and statistical mechanics. Many many beautiful theories are linked together and many intriguing things still need to be explained.

Well I think I should stop preaching here. If you want to learn more about this subject, besides the original paper above, Propp's paper [generalized domino shuffling](https://arxiv.org/abs/math/0111034) also serves as a good starting point.


## About the code

I haven't much to say about the code. You must understand the algorithm before you can understand the code, and you get understanding of the code soonly after you understand the algorithm (so please turn to the papers first).
