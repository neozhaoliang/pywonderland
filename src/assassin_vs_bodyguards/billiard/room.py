import matplotlib.pyplot as plt

from .vector import Vec2
from .wall import Wall
from .polygon import SQUARE, TRIANGLE, HEXAGON
from .guards import *


class Room:

    def __init__(self, polygon):
        self.polygon = polygon
        if polygon == "parallel":
            self.walls = [
                Wall(Vec2(-1, 10), Vec2(-1, -1)),
                Wall(Vec2(1, -1), Vec2(1, 10)),
            ]
        else:
            if polygon == "square":
                vertices = SQUARE
            elif polygon == "triangle":
                vertices = TRIANGLE
            elif polygon == "hexagon":
                vertices = HEXAGON

            self.walls = []
            for i in range(len(vertices)):
                p1 = vertices[i]
                p2 = vertices[(i + 1) % len(vertices)]
                self.walls.append(Wall(p1, p2))

    def compute_guards_positions(self, assin, target):
        if self.polygon == "square":
            return compute_guards_positions_square(self, assin, target)
        elif self.polygon == "triangle":
            return compute_guards_positions_triangle(self, assin, target)
        elif self.polygon == "hexagon":
            return compute_guards_positions_hexagon(self, assin, target)
        else:
            raise ValueError("Only square, triangle and hexagon are supported.")

    def inside(self, point):
        """
        Check if a point is inside the room.
        """
        for wall in self.walls:
            if not wall.on_positive_side(point):
                return False
        return True

    def on_segment(self, guard, start, end):
        """Check if any guard is on the segment between start and end."""
        dir = (end - start).normalize()
        inn = dir.dot(guard - start)
        proj = start + dir * inn
        return (guard - proj).length() < 1e-3

    def fold_ray_into_room(self, origin, dir, guards, target, maxhits=100):
        trajectory = [origin]
        start = Vec2(origin)
        end = start + dir * 1000
        index = -1
        while maxhits > 0:
            for wall in self.walls:
                if not wall.on_positive_side(end):
                    q = wall.intersect(start, end)
                    if q is not None:
                        for guard in guards:
                            if self.on_segment(guard, start, q):
                                trajectory.append(guard)
                                index = len(trajectory)
                                break

                        if self.on_segment(target, start, q):
                            trajectory.append(target)
                            return trajectory, index

                        trajectory.append(q)
                        start = q
                        end = wall.reflect(end)
                        maxhits -= 1

        return None, None

    def get_bounce_trajectory(self, origin, target):
        """
        Fold the ray from origin to target back into the room.
        Return the list of points where the ray bounce at the mirrors together
        with the final position of the target (the real position).
        """
        trajectory = []
        current_position = target
        while True:
            finish = True
            for wall in self.walls:
                if not wall.on_positive_side(current_position):
                    finish = False
                    q = wall.intersect(origin, current_position)
                    if q is not None:
                        trajectory.append(q)
                        origin = q
                        current_position = wall.reflect(current_position)
            if finish:
                break

        return trajectory, current_position

    def draw_trajectory(self, origin, target):
        trajectory, final_position = self.get_bounce_trajectory(origin, target)
        points = [origin] + trajectory + [final_position]
        xx, yy = zip(*points)
        lw = 0.5
        plt.plot(xx, yy, "gray", "-", lw=lw)

        guard = origin.midpoint(target)
        _, real_guard = self.get_bounce_trajectory(origin, guard)
        outside = False
        for wall in self.walls:
            if not wall.on_positive_side(guard):
                q = wall.intersect(origin, guard)
                if q is not None:
                    plt.gca().plot(*zip(q, target), "gray", linestyle="dashed", lw=lw)
                    outside = True
                    break

        if not outside:
            if len(trajectory) > 0:
                plt.gca().plot(
                    *zip(trajectory[-1], target), "gray", linestyle="dashed", lw=lw
                )

        return final_position, real_guard
