# Wilson's Uniform Spanning Tree Algorithm Animation

> Make gif animations of Wilson's uniform spanning tree algorithm and the depth-first search algorithm.

## How to use this program

Run `wilspn.py` and wait for a few seconds, you will see a `.gif` file generated in current directory. Enjoy it!

This program can be run with both python2.7+ and python3+. It's written in pure python: no third-party modules nor softwares are needed, just built-in modules `struct` and `random` and some built-in functions. I could write it faster by using `numpy` arrays but I prefer to keep the code being "pure blooded".

The code has been modified many times to make it more readable and improve the efficiency. Since Wilson's algorithm is a random algorithm, its runtime is uncertain. On my old laptop with 1.83GHzx4 Celeron processors the bitrate is about 1000kb/min, or in other words, it takes 30 seconds to generate a file of 500kb.

**Update:** I have added another script `ust.py` to show how Wilson's algorithm works. It outputs the final spanning trees as static `.png` images, not GIF animations. The code is quite short and straight-forward.


##  What is Wilson's algorithm

Wilson's algorithm comes from probability theory, it's quite important in study and is also appealing in its appearance. It chooses a random spanning tree from all such trees of a graph G (G should be finite, undirected and connected) with equal probability. Think about the crucial point here: each spanning tree has the same probability being chosen. Even for a 2d grid graph of a moderate size (for example, 50x50) the number of spanning trees is such a huge number that one can not simply list all trees first and then use a random int to sample.

The algorithm runs as follows:

1. Choose any vertex `v` as the root, maintain a tree `T`, initially `T = {v}`.

2. For any vertex `z` that is not in `T`, start a loop erased random walk from `z`, until the walk 'hits' `T` (You should see what "loop erased random walk" means from the animation), then add the resulting path of the walk to `T`.

3. repeat step 2 until all vertices of the graph are in `T`. 

For the proof of the correctness of this algorithm see Wilson's original paper:

    "Generating random spanning trees more quickly than the cover time".
    
Or the book by Russell Lyons and Yuval Peres:

	"Probability on Trees and Networks".

The maze-solving part is a bit arbitrary and you may implement any algorithm you like, I've chosen the depth first search algorithm for simplicity.


## How did it come out

This project is motivated by Mike Bostock's wonderful [Javascript animation](https://bl.ocks.org/mbostock/11357811), and also many other nice animations on his website. I learned Wilson's algorithm about 7 years ago and had the idea of writing a python version to produce GIF animations the first sight when I saw Mike's page, but rendering a GIF image which possibly consists of thousands of frames is definitely a formidable task. It's about one year ago when I occasionally touched the GIF89a specification that finally realized the approach of encoding the frames bits and bytes.


## About the code

For most time you run the script you will get an image contains 2000-3000 frames while the file size is around 200-500KB. How could one do this? There are two key points:

1. **Only update the region that has been changed** by maintaining a rectangle that defines the position of current frame. If you use some image processing tool like `ImageMagick` to unpack the example gif image into frames you will soon understand what this means.

2. **Write a GIF encoder that has minimal code length 2.** The cells in our animation has 4 possible different states hence we need only 4 colors, and 4 colors can be represented by 2 bits. With this small palette and initial code length the file size can be significantly reduced. 

Of course you have to understand the GIF89a specification first, espcially its transparent color feature and the LZW encoding algorithm.

The maze is represented by a 2D matrix like (we use a small 7x7 2d array for example)

```
m m m m m m m
m c w c w c m
m c w c w c m
m c w c w c m
m m m m m m m
```

Each character represents a square (5x5 pixels by default) in our image. `m` means "margin", these squares are served as the border of the image and **are not used in our animation.** The width of the margin can be changed (default to 2 but the example shows only 1). `w` means this a "wall", and `c` means this is a "cell". **Our grid graph contains only the cells. Walls and margins are not considered to be part of the graph.**

As the algorithm runs, the cells become connected and some walls might be set to "in tree" or "in path", but they are still **not** treated as part of the graph.


## Where to learn the GIF89a specification

The best and possibly the only reference you will need is [What's in a GIF](http://giflib.sourceforge.net/whatsinagif/index.html). You should read these three articles word by word before you can encode your gif image bits by bit.
