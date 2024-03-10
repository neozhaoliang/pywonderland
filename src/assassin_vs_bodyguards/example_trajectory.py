import matplotlib.pyplot as plt

from billiard import Room, Vec2, polygon, transform, palette


def reset(xmin, xmax, ymin, ymax):
    plt.gca().clear()
    plt.axis("off")
    plt.gca().set_aspect("equal", adjustable="box")
    plt.xlim(xmin, xmax)
    plt.ylim(ymin, ymax)


def example_parallel_trajectory():
    room = Room("parallel")

    # position of the assassin
    assassin = Vec2(-0.2, 0)
    # position of the target
    target0 = Vec2(0.66, 9)
    target1 = room.walls[0].reflect(target0)
    # get all virtual targets in some range
    targets_even = [target0 + Vec2(4 * i, 0) for i in range(-5, 6)]
    targets_odd = [target1 + Vec2(4 * i, 0) for i in range(-5, 6)]
    # get all virtual guards that block the assassin from shooting the virtual targets
    guards_even = [assassin.midpoint(x) for x in targets_even]
    guards_odd = [assassin.midpoint(x) for x in targets_odd]

    # draw the reflection trajectory of the assassin to the virtual targets
    for x in targets_even:
        _, guard = room.draw_trajectory(assassin, x)
        guards_even.append(guard)
    for x in targets_odd:
        _, guard = room.draw_trajectory(assassin, x)
        guards_odd.append(guard)

    marker_style = {"markersize": 7, "lw": 0.5, "markeredgecolor": "k"}
    plt.plot(
        *zip(*targets_even), "o", color=palette[0], **marker_style, label="Even targets"
    )
    plt.plot(
        *zip(*targets_odd), "o", color=palette[1], **marker_style, label="Odd targets"
    )
    plt.plot(*assassin, "ro", **marker_style, label="Assassin")
    plt.plot(*target0, "co", **marker_style, label="Target")
    marker_style["markersize"] = 5
    marker_style["lw"] = 0.3
    plt.plot(
        *zip(*guards_even), "o", color=palette[0], **marker_style, label="Even Guards"
    )
    plt.plot(
        *zip(*guards_odd), "o", color=palette[1], **marker_style, label="Odd Guards"
    )

    for wall in room.walls:
        wall.plot("k-", lw=1)

    xmin, xmax = -9, 9
    ymin, ymax = -0.5, 10
    ax = plt.gca()
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)
    ax.axis("off")
    # plt.legend()
    plt.tight_layout()
    plt.savefig("parallel.svg", dpi=300)


def example_square_trajectory():
    n = 8
    reset(0, n, 0, n)
    polygon.plot_square_tiling(0, n, 0, n, marker=True)
    plt.savefig("square_room.svg", bbox_inches="tight")
    n = 5
    reset(0, n, 0, n)
    room = Room("square")
    assassin = Vec2(0.1, 0.66)
    target = Vec2(0.8, 0.35)
    virtual_target = target + Vec2(4, 4)
    virtal_guard = assassin.midpoint(virtual_target)
    _, real_guard = room.draw_trajectory(assassin, virtual_target)
    polygon.plot_square_tiling(-1, n, -1, n)
    for p, color in zip([assassin, target, virtual_target], "rgy"):
        plt.plot(*p, "o", color=color, markersize=5, markeredgecolor="k")
    plt.plot(
        *zip(real_guard, virtal_guard),
        "o",
        color="gray",
        markersize=4,
        markeredgecolor="k",
        lw=0.5
    )
    plt.savefig("square_room_trajectory.svg", bbox_inches="tight")


def example_triangle_trajectory():
    n = 7
    reset(-0.5, n - 1, -0.5, n - 1)
    polygon.plot_triangle_tiling(-n, n, -n, n, marker=True)
    plt.savefig("triangle_room.svg", bbox_inches="tight")
    reset(-0.5, n - 1, -0.5, n - 1)
    room = Room("triangle")
    assassin = Vec2(0.3, 0.35)
    target = Vec2(0.68, 0.24)
    virtual_target = target + transform.triangle_to_cartesian(1, 4)
    virtal_guard = assassin.midpoint(virtual_target)
    _, real_guard = room.draw_trajectory(assassin, virtual_target)
    polygon.plot_triangle_tiling(-5, n + 1, -5, n + 1)
    for p, color in zip([assassin, target, virtual_target], "rgy"):
        plt.plot(*p, "o", color=color, markersize=5, markeredgecolor="k")
    plt.plot(
        *zip(real_guard, virtal_guard),
        "o",
        color="gray",
        markersize=4,
        markeredgecolor="k",
        lw=0.5
    )
    plt.savefig("triangle_room_trajectory.svg", bbox_inches="tight")


def example_hexagon_trajectory():
    n = 5
    reset(1 - n, n - 1, 1 - n, n - 1)
    polygon.plot_hexagon_tiling(-n - 3, n + 3, -n - 3, n + 3, marker=True)
    plt.savefig("hexagon_room.svg", bbox_inches="tight")
    reset(-0.5, n - 1, -0.5, n - 1)
    room = Room("hexagon")
    assassin = Vec2(0.1, 1.4)
    target = Vec2(0.55, 0.24)
    virtual_target = target + transform.triangle_to_cartesian(1, 4)
    virtal_guard = assassin.midpoint(virtual_target)
    final_position, real_guard = room.draw_trajectory(assassin, virtual_target)
    polygon.plot_hexagon_tiling(-5, n + 1, -5, n + 1)
    for p, color in zip([assassin, target, virtual_target, final_position], "rgyc"):
        plt.plot(
            *p,
            "o",
            color=color,
            markersize=5,
            markeredgecolor="k",
            label=(
                "Assassin"
                if color == "r"
                else (
                    "Target"
                    if color == "g"
                    else (
                        "Virtual target"
                        if color == "y"
                        else "Virtual target in the room"
                    )
                )
            )
        )
    plt.plot(
        *zip(real_guard, virtal_guard),
        "o",
        color="gray",
        markersize=4,
        markeredgecolor="k",
        lw=0.5
    )
    plt.legend()
    plt.savefig("hexagon_room_trajectory.svg", bbox_inches="tight")


example_parallel_trajectory()
example_square_trajectory()
example_triangle_trajectory()
example_hexagon_trajectory()
