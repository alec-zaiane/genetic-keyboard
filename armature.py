"""Bones and armature for handling hand and finger movement."""
from __future__ import annotations
from typing import Any, Optional
from linalg import Vec2, Transform2dHomogeneous as T2D
class Bone:
    """A bone object exists in 2d and has a length and rotation, the rotation and position are relative to the parent bone's end position."""
    def __init__(self, name:str, pos_offset: Vec2, length: float, rotation_rad:float, parent:Optional[Bone]=None):
        """Create a new Bone object.

        Args:
            name (str): The name of the bone.
            pos_offset (Vec2): Offset from the parent bone's end position, this takes into account the parent bone's rotation.
            length (float): how long the bone is.
            rotation_rad (float): what angle the bone is relative to the parent bone.
        """
        self._name = name
        self._pos_offset = pos_offset
        self._length = length
        self._rotation_rad = rotation_rad
        self.parent:Optional[Bone] = None
        
    @property
    def name(self) -> str:
        """The name of the bone."""
        return self._name
        
    def get_transform_local(self) -> T2D:
        """Get the transform of this bone relative to the parent bone, or the world if there is no parent."""
        return T2D.new_translation_matrix(self._pos_offset) @ T2D.new_rotation_matrix(self._rotation_rad)
    
    def get_transform_world(self) -> T2D:
        """Get the transform of this bone relative to the world."""
        if self.parent is None:
            return self.get_transform_local()
        else:
            return self.parent.get_transform_world() @ self.get_transform_local()
        
    def get_worldspace_positions(self) -> tuple[Vec2, Vec2]:
        """Get the start and end positions of this bone relative to the world."""
        transform = self.get_transform_world()
        return (transform.multiply_point(Vec2(0, 0)), transform.multiply_point(Vec2(self._length, 0)))
        
        
class Armature:
    """Hold a list of bones and allow them to be moved, also has some helper functions."""
    def __init__(self, bones:Optional[list[Bone]]=None):
        self._bones:dict[str, Bone] = {}
        if bones is not None:
            for bone in bones:
                self.add_bone(bone)
        
    def add_bone(self, bone:Bone):
        """Add a bone to the armature

        Args:
            bone (Bone): the bone to add
            
        Raises:
            ValueError: if a bone with the same name already exists.
            KeyError: if the bone's parent does not exist in the armature already.
        """
        if bone.name in self._bones:
            raise ValueError(f"Bone with name {bone.name} already exists.")
        if bone.parent is not None and bone.parent.name not in self._bones:
            raise KeyError(f"Bone with name {bone.parent.name} does not exist in the armature.")
        self._bones[bone.name] = bone
        
    def get_worldspace_positions(self) -> dict[str, tuple[Vec2, Vec2]]:
        """Get the worldspace positions of all bones in the armature."""
        return {name: bone.get_worldspace_positions() for name, bone in self._bones.items()}
        
    def __getattribute__(self, __name: str) -> Any:
        """Get a bone by name."""
        if __name.startswith("_"):
            return super().__getattribute__(__name)
        else:
            return self._bones[__name]
        
    
        
    
        