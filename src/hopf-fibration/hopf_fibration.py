"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Draw Hopf fibration using POV-Ray
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

See "https://en.wikipedia.org/wiki/Hopf_fibration"

In this script the data of the fibers are computed
in python and exported to POV-Ray.

Usage: simply run

    python hopf_fibration.py

Make sure POV-Ray is installed and set the path to the
executable file in `POV-COMMAND`.

"""
import subprocess
import numpy as np


POV_COMMAND = "povray"


def pov_vector(v):
    """Convert a vector to POV-Ray format.
    """
    return "<{}>".format(", ".join([str(x) for x in v]))


def pov_matrix(M):
    """Convert a 3x3 matrix to a POV-Ray array.
    """
    return "array[3] {{ {} }}\n".format(", ".join([pov_vector(v) for v in M]))


def normalize(v):
    """Normalize a vector `v`.
    """
    return np.array(v) / np.linalg.norm(v)


def norm2(v):
    """Return squared Euclidean norm of a vector.
    """
    return sum([x*x for x in v])


def proj3d(v):
    """Stereographic projection of a 4d vector with pole at (0, 0, 0, 1).
    """
    v = normalize(v)
    x, y, z, w = v
    return np.array([x, y, z]) / (1 + 1e-8 - w)


def get_circle(A, B, C):
    """Compute the center, radius and normal vector of the 3d circle
       passes through 3 given points (A, B, C).
       See "https://en.wikipedia.org/wiki/Circumscribed_circle"
    """
    a = A - C
    b = B - C
    axb = np.cross(a, b)
    center = C + np.cross((norm2(a) * b - norm2(b) * a), axb) \
             / (2 * norm2(axb))
    radius = np.sqrt(norm2(a) * norm2(b) * norm2(a - b) \
             / (4 * norm2(axb)))
    normal = normalize(axb)
    return center, radius, normal


def hopf_inverse(phi, psi, theta):
    """Return the preimage of a point (phi, psi) on S^2, this preimage
       is a circle on S^3 and can be parameterized by `theta`.

       A point on S^2 can be parameterized by

       x = sin(phi) * cos(psi)
       y = sin(phi) * sin(psi)
       z = cos(phi)

       where 0 <= phi <= pi and 0 <= psi <= 2*pi.
    """
    return np.array([np.cos((theta + psi) / 2) * np.sin(phi / 2),
                     np.sin((theta + psi) / 2) * np.sin(phi / 2),
                     np.cos((theta - psi) / 2) * np.cos(phi / 2),
                     np.sin((theta - psi) / 2) * np.cos(phi / 2)])


def transform_matrix(v):
    """Return a 3x3 orthogonal matrix that transforms y-axis (0, 1, 0)
       to a vector `v`. This function is for POV-Ray rendering since
       in POV-Ray by default a "torus" object is on the xz-plane.
    """
    y = normalize(v)
    a, b, c = y
    if a == 0:
        x = (1, 0, 0)
    else:
        x = normalize([-b, a, 0])
    z = np.cross(x, y)
    return np.array([x, y, z])


def export_fiber(phi, psi, color):
    """Export the data of a fiber to POVv-Ray format.
    """
    A, B, C = [proj3d(hopf_inverse(phi, psi, theta))
               for theta in (0, np.pi/2, np.pi)]
    center, radius, normal = get_circle(A, B, C)
    matrix = transform_matrix(normal)

    return "Torus({}, {}, {}, {})\n".format(pov_vector(center),
                                            radius,
                                            pov_matrix(matrix),
                                            pov_vector(color))


def main():
    """Render a flower pattern of fibers.
    """
    N = 7  # controls the number of petals
    A = 0.5  # controls the fattness of the petals
    B = -np.pi / 7  # controls the amplitude of the polar angle range
    P = np.pi / 2  # controls latitude of the flower

    with open("./povray/torus-data.inc", "w") as f:
        for t in np.linspace(0, 1, 200):
            phi = B * np.sin(N * 2 * np.pi * t) + P
            psi = np.pi * 2 * t + A * np.cos(N * 2 * np.pi * t)
            color = np.random.random(3)
            f.write(export_fiber(phi, psi, color))

    subprocess.call("cd povray && povray hopf_fibers.ini", shell=True)


if __name__ == "__main__":
    main()
