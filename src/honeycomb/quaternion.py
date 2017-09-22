import numpy as np


class Quaternion(np.ndarray):
    """
    A quaternion is represented as [w, x, y, z] where w is the scalar part
    and [x, y, z] is the vector part. w, x, y, z are all floating numbers.
    """
    
    # tolerance for comparing if two quaternions are equal.
    _epsilon = 1e-6
    
    def __new__(cls, vec=(1, 0, 0, 0)):
        """
        We have no type checking here for simplicity. Here `vec` should be a 1-d list
        of length 3 or 4. If len(vec) is 3 then the vector part is initialized by `vec`.
        """
        q = np.zeros(4, dtype=np.float).view(cls)
        q[4 - len(vec): ] = vec
        return q
    
    @staticmethod
    def from_complex(z):
        return Quaternion([0, z.real, z.imag, 0])
    
    def __complex__(self):
        """Convert the x, y components to a complex number."""
        return complex(self[1], self[2])    
        
    def __abs__(self):
        """Called by `abs(q)`."""
        return np.linalg.norm(self)
    
    def __eq__(self, other):
        # if two quaternions p, q both contain `NaN` then they are equal.
        if any(np.isnan(self)) and any(np.isnan(other)):
            return True
        
        # if exactly one of them contains `Nan` then they are unequal. 
        if any(np.isnan(self)) or any(np.isnan(other)):
            return False

        # else they are equal if and only if for each component i, p[i] and q[i] are
        # both `np.inf` or `-np.inf` or satisfy abs(p[i] - q[i]) <= Quaternion._epsilon.
        for this, that in zip(self, other):
            if this == that:
                continue
            if abs(this - that) > Quaternion._epsilon:
                return False

        return True
    
    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __lt__(self, other):
        """
        Here we use a lexical order to compare two quaternions p, q. 
        Let i be the first component they differ: abs(p[i] - q[i]) > Quaternion._epsilon.
        if p[i] > q[i] + Quaternion._epsilon then p > q;
        if p[i] < q[i] - Quaternion._epsilon then p < q.
        if there is no such i then they are equal.
        """
        for this, that in zip(self, other):
            if this < that - Quaternion._epsilon:
                return True
        return False
    
    def __gt__(self, other):
        """See the doc for `__lt__`."""
        for this, that in zip(self, other):
            if this > that - Quaternion._epsilon:
                return True
        return False
    
    def __ge__(self, other):
        return not self.__lt__(other)

    def __le__(self, other):
        return not self.__gt__(other)
    
    def __hash__(self):
        """
        We should try to ensure that equal quaternions have the same hash value.
        Note two quaternions are equal if and only if all of their components
        are the same if rounded to the accuracy determined by `Quaternion._epsilon`,
        so we simply use the hash value of this rounded array.
        """
        if any(np.isnan(self)):
            return hash(np.NaN)
        else:
            decimals = int(np.log10(1.0 / Quaternion._epsilon))
            return hash(tuple(self.round(decimals)))
    
    def __bool__(self):
        """
        Called by `bool(q)` in the syntax `if q`. If q contains `NaN` or its components
        are all very close to zero then it's treated as invalid.
        """ 
        if any(np.isnan(self)):
            return False
        
        elif max(np.absolute(self)) > Quaternion._epsilon:
            return True
        
        else:
            return False
        
    __nonzero__ = __bool__    # for python2
    
    def __mul__(self, other):
        """
        Multipication of a quaternion with a scalar or another quaternion.
        We do not need to implement `__rmul__` because numpy has already did it for us.
        """
        w1, x1, y1, z1 = self
        if np.isscalar(other):
            return Quaternion([w1*other, x1*other, y1*other, z1*other])

        elif isinstance(other, Quaternion):
            w2, x2, y2, z2 = other
            return Quaternion([w1*w2 - x1*x2 - y1*y2 - z1*z2,
                               w1*x2 + w2*x1 + y1*z2 - z1*y2,
                               w1*y2 + y1*w2 + z1*x2 - x1*z2,
                               w1*z2 + z1*w2 + x1*y2 - y1*x2])

        else:
            raise TypeError("Cannot multiply a quaternion with this input.")
            
    def conjugate(self):
        w, x, y, z = self
        return Quaternion([w, -x, -y, -z])
    
    def inverse(self):
        return self.conjugate() / sum(self**2)
    
    def __div__(self, other):
        w, x, y, z = self
        if np.isscalar(other):
            return Quaternion([w/other, x/other, y/other, z/other])
                    
        elif isinstance(other, Quaternion):
            return self * other.inverse()
    
        else:
            raise TypeError("cannot divide a quaternion by this input.")

    def __rdiv__(self, other):
        return other * self.inverse()
     
    def normalize(self):
        """Invalid quaternions cannot be normalized."""
        if not self:
            raise ValueError("can not normalize an invalid quaternion.")
        else:
            self /= abs(self)
            return self
    
    def angle_to(self, other):
        """Compute the angle between two quaternions."""
        cos_angle = np.dot(self, other) / (abs(self) * abs(other))        
        # Floating point errors would make `arccos` return `NaN`.
        cos_angle = np.clip(cos_angle, -1.0, 1.0)
        return np.arccos(cos_angle)

    def cross(self, other):
        """
        By using negative indices `other` can be either a quaternion or a 3-d vector.
        The returned type is a 3-d vector.
        """
        return Quaternion(np.cross(self[-3:], other[-3:]))

    def perpendicular(self):
        """
        Return a vector (not unique) that is perpendicular to this one.
        The result is normalized.
        """
        if not self:
            return Quaternion([0, 0, 0, 0])

        result = self.cross([0, 0, 1])    # cross product with the z-axis.
        
        # if the vector part of self is parellel with z-axis then `result` would be zero,
        # use x-axis instead.
        if not result:
            result = self.cross([1, 0, 0])

        return result.normalize()
    
    def rotate_in_xy_plane(self, angle, center=complex(0, 0)):
        """Rotate in the xy-plane about a center."""
        u = complex(self) - center
        u *= complex(np.cos(angle), np.sin(angle))
        u += center
        self[1], self[2] = u.real, u.imag

    def central_project(self, camera_distance):
        """
        Project to the xy-plane. Here we assume the coordinate system is right-handed and
        the viewer is located at the positive half of the z-axis and look at the origin.
        Objects "behind" or "nearly behind" the viewer will be discarded.
        """
        denom = camera_distance - self[3]
        denom = max(denom - Quaternion._epsilon, 0)
        return Quaternion([0,
                           self[1] * camera_distance / denom,
                           self[2] * camera_distance / denom,
                           0])
    
    def project_to_3d(self, camera_distance):
        denom = camera_distance - self[0]
        denom = max(denom - Quaternion._epsilon, 1e-4)
        return Quaternion(np.asarray(self[1:]) * camera_distance / denom)
    
    @staticmethod
    def from_axis_angle(axis, angle):
        """
        Return the quaternion that represents the rotation specified by `(axis, angle)`.
        `axis` must be a non-zero 3-d vector.
        """
        x, y, z = np.asarray(axis) / np.linalg.norm(axis)
        halfangle = angle / 2.0
        return Quaternion([np.cos(halfangle),
                           np.sin(halfangle) * x,
                           np.sin(halfangle) * y,
                           np.sin(halfangle) * z])
    
    def to_axis_angle(self):
        self.normalize()
        w, x, y, z = self
        angle = 2.0 * np.arccos(w)
        axis = np.asarray([x, y, z])
        axis /= np.linalg.norm(axis)
        return axis, angle
    
    def rotate_vector(self, v):
        """
        Rotate a 3-d vector `v` with this quaternion.The returned type is a quaternion.
        """
        self.normalize()
        v_new = self * Quaternion(v) * self.conjugate()
        v_new[0] = 0
        return v_new
    
    def to_matrix(self):
        """Return the 3x3 matrix representation of this quaternion."""
        self.normalize()
        w, x, y, z = self
        return np.array([[1-2*y*y-2*z*z, 2*x*y-2*w*z, 2*x*z+2*y*w],
                         [2*x*y+2*w*z, 1-2*x*x-2*z*z, 2*y*z-2*w*x],
                         [2*x*z-2*y*w, 2*y*z+2*x*w, 1-2*x*x-2*y*y]])
