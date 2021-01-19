import helpers


class DihedralFace(object):

    """
    A dihedral face in the tiling is a 2d polygon obtained by applying
    a word on a fundamental face, where a fundamental face is generated
    by two simple reflections and its center is one of the vertices of
    the fundamental triangle.
    """

    def __init__(self, word, center, coords, type, geometry):
        """
        word: the word that transforms the fundamental domain to this polygon.
        center: coordinates of the center of this polygon.
        coords: coordinates of the vertices of this polygon.
        type: type of this face (0 or 1).
        """
        self.word = word
        self.center = center
        self.coords = coords
        self.type = type
        if geometry == "euclidean":
            self.normalize_func = lambda p: p / p[-1]
        else:
            self.normalize_func = helpers.normalize

    def get_alternative_domains(self):
        """
        This function is used to color the faces in a checker fashion.
        We put the domains transformed by words of even and odd length
        into two different lists. The face may be a regular m-polygon
        (which has type 0) or an uniform 2m-polygon (which has type 1),
        where 2pi/m is the angle between the two mirrors.
        """
        domain1 = []
        domain2 = []
        for i, p in enumerate(self.coords):
            # the two adjacent vertices and the middle points with them
            q1 = self.coords[(i + 1) % len(self.coords)]
            q2 = self.coords[i - 1]
            m1 = self.normalize_func((p + q1) / 2)
            m2 = self.normalize_func((p + q2) / 2)

            if self.type:
                if (len(self.word) + i) % 2 == 0:
                    domain1.append((m1, p, m2, self.center))
                else:
                    domain2.append((m1, p, m2, self.center))

            else:
                if len(self.word) % 2 == 0:
                    domain1.append((m1, p, self.center))
                    domain2.append((m2, p, self.center))
                else:
                    domain1.append((m2, p, self.center))
                    domain2.append((m1, p, self.center))

        return domain1, domain2
