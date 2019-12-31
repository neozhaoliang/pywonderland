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
5. Then it computes the stabilizing subgroup of the initial vertex and its coset representatives, and uses orbit-stabilizing theorem to transform the initial vertex to get all other vertices.
6. Simialr for edges and faces.
7. All these computations above only use integer arithmetic, no floating error invovled.
8. For triangle groups it computes the data quite fast.
9. Finally draw the tiling.

It's still a quite straight and dirty implementation so there's a long way to improve it.

TODO:

1. snub and Catalan tilings.
2. lots of more fancy features.
3. a detailed doc explains the math.
4. Escher tiling using a user input svg image.
