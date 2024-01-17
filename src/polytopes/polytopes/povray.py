"""
Some POV-Ray stuff.
"""


def concat(arr, sep=",\n", border=None):
    """Concatenate items in an array using seperator `sep`.
    """
    if border is None:
        return sep.join(str(x) for x in arr)
    return border.format(sep.join(str(x) for x in arr))


def pov_vector(v):
    """Convert a vector to POV-Ray format. e.g. (x, y, z) --> <x, y, z>.
    """
    return concat(v, sep=", ", border="<{}>")


def pov_vector_array(vectors):
    """Convert a list of vectors to POV-Ray format, e.g.
    [(x, y, z), (a, b, c), ...] --> array[n] {<x, y, z>, <a, b, c>, ...}.
    """
    n = len(vectors)
    return "array[{}]{{\n{}}}".format(n, concat(pov_vector(v) for v in vectors))


def pov_index_array1d(arr1d):
    """Convert a 1d array to POV-Ray string, e.g. (1, 2, 3) --> array[3] {1, 2, 3}
    """
    n = len(arr1d)
    return "array[{}] {{\n{}}}".format(n, concat(arr1d, sep=", "))


def pov_index_array2d(arr2d):
    """
    Convert a mxn 2d array to POV-Ray format, e.g.
    [(1, 2), (3, 4), (5, 6)] --> arrar[3][2] {{1, 2}, {3, 4}, {5, 6}}.
    """
    dim1 = len(arr2d)
    dim2 = len(arr2d[0])
    return "array[{}][{}] {{\n{}}}".format(
        dim1, dim2, concat(concat(arr, sep=", ", border="{{{}}}") for arr in arr2d)
    )


def pov_index_array3d(arr3d):
    """Convert a 3d array to an array of 2d arrays in POV-Ray format.
    """
    n = len(arr3d)
    return "array[{}] {{\n{}}}".format(
        n, concat(pov_index_array2d(arr2d) for arr2d in arr3d)
    )


def export_polytope_data(P):
    """Return the data of a polytope `P` in POV-Ray format.
    """
    vert_data = pov_vector_array(P.vertices_coords)
    edge_data = pov_index_array3d(P.edge_indices)
    face_data = pov_index_array3d(P.face_indices)
    return vert_data, edge_data, face_data