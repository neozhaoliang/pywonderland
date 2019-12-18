# Uniform tilings and automata of Coxeter groups

This is a very first version of a very complicated program: draw uniform Euclidean/Spherical/Hyperbolic tilings using automata of Coxeter groups. The purpose of this project is:

1. Render 2d tilings in svg format.
2. Render 3d tilings in POV-Ray.

I have finished the math stuff (most difficult part in the code) and attached a few examples for illustrating the procedure. You can run the example_*.py scripts to see the results.

Basically the program knows everything of a tiling before you draw it:

1. It firstly builds the Coxeter group of the tiling.
2. It knows how to do multiplicaitons in the group.
3. It knows how to generate words in the group.
4. It knows how to find a set of coset representatives of a standard parabolic subgroup.
5. It knows the stabilizing subgroup of the initial vertex, and its coset representatives, and the coset table of these representatives.
6. It knows the stabilizing subgroup of an initial edge, and its coset representatives, and using orbit-stabilizer theorem to transform it to other edges.
7. Simialr for the faces.
8. All these computations above only use integer arithmetic, no floating error invovled.
9. For triangle groups it computes the data quite fast.
10. Finally draw the tiling.

It's still a quite straight and dirty implementation so there's a long way to improve it.

TODO:

1. 3d hyperbolic honeycombs.
2. snub, star, Catalan tilings.
3. lots of more fancy features.
4. a detailed doc explains the math.

**Update 2019/12/19**: I find that there are some bugs in the Euclidean case, and since I have also decided to draw 2d spherical tilings in svg format, hence I temporarily removed the code for drawing Euclidean and spherical cases. I will add them back as soon as possible.

Of course there are also a few minor bugs in the hyperbolic case, but you can still run the code to see the power of this new approach of drawing tilings.
