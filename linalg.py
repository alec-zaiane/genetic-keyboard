"""2d vector class to make math easier elsewhere, as well as a 2d homogeneous transformation matrix class."""
from __future__ import annotations
import math
import numpy as np

class Vec2:
    """2d vector
    """    
    def __init__(self, x:float, y:float):
        self.x = x
        self.y = y
        
    @property
    def length(self):
        return math.sqrt(self.x**2 + self.y**2)

    def __add__(self, other:Vec2) -> Vec2:
        return Vec2(self.x + other.x, self.y + other.y)

    def __sub__(self, other:Vec2) -> Vec2:
        return Vec2(self.x - other.x, self.y - other.y)

    def __truediv__(self, other:float) -> Vec2:
        return Vec2(self.x / other, self.y / other)

    def __mul__(self, other:float) -> Vec2:
        return Vec2(self.x * other, self.y * other)

    def rotate(self, angle:float) -> Vec2:
        """Rotate this vector by `angle` radians."""
        return Vec2(self.x * math.cos(angle) - self.y * math.sin(angle), self.x * math.sin(angle) + self.y * math.cos(angle))

    def dot(self, other:Vec2) -> float:
        """Dot product of this vector with `other`."""
        return self.x * other.x + self.y * other.y
    
    def __str__(self):
        return f"Vec2({self.x}, {self.y})"
    
    @classmethod
    def unit_vector(cls, angle:float) -> Vec2:
        """Create a unit vector with the given angle in radians."""
        return Vec2(math.cos(angle), math.sin(angle))
    
    @classmethod
    def unit_vector_deg(cls, angle:float) -> Vec2:
        """Create a unit vector with the given angle in degrees."""
        return Vec2.unit_vector(math.radians(angle))
    
class Transform2dHomogeneous:
    """2d homogeneous transformation matrix"""
    def __init__(self):
        self.matrix = np.identity(3)
        
    @classmethod
    def new_translation_matrix(cls, translation:Vec2) -> Transform2dHomogeneous:
        """Create a new translation matrix."""
        mat = cls()
        mat.matrix[0, 2] = translation.x
        mat.matrix[1, 2] = translation.y
        return mat
    
    @classmethod
    def new_rotation_matrix(cls, rotation_rad:float) -> Transform2dHomogeneous:
        """Create a new rotation matrix., rotation is in radians."""
        mat = cls()
        mat.matrix[0, 0] = math.cos(rotation_rad)
        mat.matrix[0, 1] = -math.sin(rotation_rad)
        mat.matrix[1, 0] = math.sin(rotation_rad)
        mat.matrix[1, 1] = math.cos(rotation_rad)
        return mat

    @classmethod
    def new_rotation_matrix_deg(cls, rotation_deg:float) -> Transform2dHomogeneous:
        """Create a new rotation matrix., rotation is in degrees."""
        return cls.new_rotation_matrix(math.radians(rotation_deg))
    
        

    def chain_translate(self, translation:Vec2) -> Transform2dHomogeneous:
        """Return a new transformation matrix that is the result of translating by `translation`."""
        to_multiply = Transform2dHomogeneous.new_translation_matrix(translation)
        # now just matmul them as they are both numpy arrays
        mat = Transform2dHomogeneous()
        mat.matrix = self.matrix @ to_multiply.matrix
        return mat
    
    def chain_rotate(self, rotation_rad:float) -> Transform2dHomogeneous:
        """Return a new transformation matrix that is the result of rotating by `rotation_rad` radians."""
        to_multiply = Transform2dHomogeneous.new_rotation_matrix(rotation_rad)
        mat = Transform2dHomogeneous()
        mat.matrix = self.matrix @ to_multiply.matrix
        return mat
    
    def chain_rotate_deg(self, rotation_deg:float) -> Transform2dHomogeneous:
        """Return a new transformation matrix that is the result of rotating by `rotation_deg` degrees."""
        return self.chain_rotate(math.radians(rotation_deg))

        