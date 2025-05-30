"""
This script visualizes the unique simple perfect square of order 21, 
the lowest possible order, discovered in 1978 by A. J. W. Duijvestijn.

The square is composed of 21 smaller squares whose side lengths sum to 112.

Reference:
    http://www.squaring.net/sq/ss/spss/spss.html
"""
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.cm import tab20 as colormap

plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["text.usetex"] = True

squares = [
    {"x": 63, "y": 60, "size": 2}, 
    {"x": 29, "y": 33, "size": 4}, 
    {"x": 82, "y": 60, "size": 6}, 
    {"x": 63, "y": 53, "size": 7},
    {"x": 85, "y": 77, "size": 8}, 
    {"x": 54, "y": 53, "size": 9}, 
    {"x": 82, "y": 66, "size": 11}, 
    {"x": 50, "y": 62, "size": 15}, 
    {"x": 54, "y": 37, "size": 16}, 
    {"x": 65, "y": 60, "size": 17}, 
    {"x": 70, "y": 42, "size": 18},     
    {"x": 93, "y": 66, "size": 19}, 
    {"x": 88, "y": 42, "size": 24},
    {"x": 29, "y": 37, "size": 25}, 
    {"x": 85, "y": 85, "size": 27}, 
    {"x": 0, "y": 33, "size": 29},
    {"x": 0, "y": 0, "size": 33},
    {"x": 50, "y": 77, "size": 35}, 
    {"x": 33, "y": 0, "size": 37},  
    {"x": 70, "y": 0, "size": 42}, 
    {"x": 0, "y": 62, "size": 50}
]


fig, ax = plt.subplots(figsize=(8, 8))
ax.axis([-1, 113, -1, 113])
ax.set_aspect("equal")
ax.axis("off")

for index, square in enumerate(squares):
    x, y, size = square["x"], square["y"], square["size"]
    fc = colormap(index % 20)
    rect = patches.Rectangle((x, y), size, size, lw=1, edgecolor="black", facecolor=fc)
    ax.add_patch(rect)
    ax.text(x + size / 2, y + size / 2, f"${size}$",
            ha="center", va="center", fontsize=max(size * 2, 10), color="white", fontweight="bold")

plt.savefig("perfect_squared_square.svg", bbox_inches="tight", transparent=True)
