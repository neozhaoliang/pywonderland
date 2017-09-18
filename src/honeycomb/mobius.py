import numpy as np


class Mobius(object):

    def __init__(self, mat):
        self.mat = np.array(mat).astype(np.complex)

    def __str__(self):
        return str(self.mat)

    def __mul__(self, M):
        return Mobius(np.dot(self.mat, M.mat))
    
    @staticmethod
    def identity():
        return Mobius([[1, 0],
                       [0, 1]])

    @staticmethod
    def scale(c):
        return Mobius([[c, 0],
                       [0, 1]])

    def normalize(self):
        det = np.sqrt(np.linalg.det(self.mat))
        self.mat /= det
        return self
