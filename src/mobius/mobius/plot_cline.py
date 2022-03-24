import matplotlib.pyplot as plt


def plot_line(ax, normal, offset, **style):
    # line equation: Ax + By = C
    A, B = normal.real, normal.imag
    C = offset
    x0 = C * A
    y0 = C * B
    L = 10
    sx = x0 - B * L
    sy = y0 + A * L
    ex = x0 + B * L
    ey = y0 - A * L
    line, = ax.plot([sx, ex], [sy, ey], **style)
    return line


def plot_circle(ax, center, radius, **style):
    patch = plt.Circle(
        (center.real, center.imag), radius, **style
    )
    ax.add_patch(patch)
    return patch


def plot_cline(ax, C, line_style, circle_style):
    cline_type, center, radius = C.get_params()
    if cline_type == "circle":
        return plot_circle(ax, center, radius, **circle_style)
    elif cline_type == "line":
        return plot_line(ax, center, radius, **line_style)
    else:
        raise NotImplementedError("Cannot plot this cline")
