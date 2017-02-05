'''
Animating the Lorenz system with matplotlib's animation module.
Code adapted from 

    "https://jakevdp.github.io/blog/2013/02/16/animating-the-lorentz-system-in-3d/"
'''

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation
from scipy.integrate import odeint  
from mpl_toolkits.mplot3d import Axes3D  


# constants for Lorenz system
alpha, beta, gamma = 10.0, 8/3.0, 28.0

num_trajectories = 20


def derivative(point, t):
    x, y, z = point
    return [alpha * (y - x), x * (gamma - z) - y, x * y - beta * z]


fig = plt.figure(figsize=(6, 4.8), dpi=100)
ax = fig.add_axes([0, 0, 1, 1], projection='3d', xlim=(-25, 25),
                  ylim=(-35, 35), zlim=(5, 55), aspect=1)
ax.view_init(30, 0)
ax.axis('off')

lines = []
points = []
colors = plt.cm.jet(np.linspace(0, 1, num_trajectories))
  
for c in colors:
    lines.extend(ax.plot([], [], '-', color=c))
    points.extend(ax.plot([], [], 'o', color=c))
    

x0 = -15 + 30 * np.random.random((num_trajectories, 3))
t = np.linspace(0, 4, 1001)
x_t = np.array([odeint(derivative, point, t) for point in x0])

    
def init():
    for line, point in zip(lines, points):
        line.set_data([], [])
        line.set_3d_properties([])

        point.set_data([], [])
        point.set_3d_properties([])
    return lines + points


def animate(i):
    # accelarate the animation
    i = 2*i % x_t.shape[1]
    
    for line, point, x_j in zip(lines, points, x_t):
        x, y, z = x_j[:i].T

        line.set_data(x, y)
        line.set_3d_properties(z)
        
        # note that plot() receives a list parameter so we have
        # to write x[-1:] instead of x[-1]!
        point.set_data(x[-1:], y[-1:]) 
        point.set_3d_properties(z[-1:])

    ax.view_init(30, 0.3*i)
    fig.canvas.draw()
    return lines + points 



def main():
    anim = FuncAnimation(fig, animate, init_func=init, interval=5, 
                         frames=500, blit=True)
    #fig.show()
    anim.save('lorenz.mp4', writer='ffmpeg', fps=30, bitrate=1000, dpi=300, codec='libx264')


if __name__ == '__main__':
    main()
