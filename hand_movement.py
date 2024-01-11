"""Simple hand heuristics for estimating posing difficulty"""
from dataclasses import dataclass
from typing import Any
import math

@dataclass
class HandShape:
    """hand shape, used for movement estimation
    default values are probably alright
    """
    
    # wrist params
    wrist_inwards_bound: float = 15 # in degrees
    """How many degrees can the wrist go inwards (towards the body), starting from a position where the palm is down and the fingers are parallel to the forearm"""
    wrist_inwards_difficulty: float = 1
    """How 'hard' is it to move the wrist inwards compared to other hand movements, this will be minimized when calculating the best movement to press a key"""
    wrist_outwards_bound: float = 30 # in degrees
    """How many degrees can the wrist go outwards (away from the body), starting from a position where the palm is down and the fingers are parallel to the forearm"""
    wrist_outwards_difficulty: float = 0.5
    """How 'hard' is it to move the wrist outwards compared to other hand movements, this will be minimized when calculating the best movement to press a key"""
    wrist_rest_position: float = 10
    """How many degrees is the wrist rotated outwards when the hand is in a resting position, as most people don't have their fingers parallel to their forearm when resting their hand"""
    
    # finger root positions
    # all measurements are in mm from the wrist's centerpoint
    # positive y is away from the body, positive x is toward the thumb
    # ascii taken from https://ascii.co.uk/art/hand
    # +y
    # |          /"\
    # |      /"\|\./|/"\
    # |     |\./|   |\./|
    # |     |   |   |   |
    # |     |   |>~<|   |/"\
    # |     |>~<|   |>~<|\./|
    # |     |   |   |   |   |
    # | /~T\|   |   =[@]=   |
    # | |_/ |   |   |   |   |
    # | |   | ~   ~   ~ |   |
    # | |~< |             ~ |
    # | |   '               |
    # | \                   |
    # |  \                 /
    # |   \               /
    # |    \.            /
    # |      |          |
    # |      |          |
    # -y
    #
    #   +x ----------------- -x
    thumb_root_position: tuple[float,float] = (40, 20)
    """(x,y) position of the thumb's root joint, relative to the wrist's centerpoint, in mm"""
    index_root_position: tuple[float,float] = (19, 80)
    """(x,y) position of the index finger's root joint, relative to the wrist's centerpoint, in mm"""
    middle_root_position: tuple[float,float] = (3, 82)
    """(x,y) position of the middle finger's root joint, relative to the wrist's centerpoint, in mm"""
    ring_root_position: tuple[float,float] = (-16, 80)
    """(x,y) position of the ring finger's root joint, relative to the wrist's centerpoint, in mm"""
    pinky_root_position: tuple[float,float] = (-30, 78)
    
    # finger lengths
    thumb_length: float = 45
    """Length of the thumb, in mm"""
    index_length: float = 70
    """Length of the index finger, in mm"""
    middle_length: float = 73
    """Length of the middle finger, in mm"""
    ring_length: float = 71
    """Length of the ring finger, in mm"""
    pinky_length: float = 65
    """Length of the pinky finger, in mm"""
    
    
    # splay characteristics
    # index and middle finger splay to the thumb side, ring and pinky splay to the pinky side
    # splay has a cost associated with it too, smaller angles are less costly, but it's mostly easier than moving the wrist
    # splay is measured in degrees, cost is arbitrary units, which are multiplied by the splay angle
    
    index_max_splay: float = 30
    """Maximum angle the index finger can splay, in degrees"""
    index_splay_cost: float = 0.3
    """Cost of splaying the index finger, in arbitrary units"""
    middle_max_splay: float = 20
    """Maximum angle the middle finger can splay, in degrees"""
    middle_splay_cost: float = 0.35
    """Cost of splaying the middle finger, in arbitrary units"""
    ring_max_splay: float = 23
    """Maximum angle the ring finger can splay, in degrees"""
    ring_splay_cost: float = 0.4
    """Cost of splaying the ring finger, in arbitrary units"""
    pinky_max_splay: float = 43
    """Maximum angle the pinky finger can splay, in degrees"""
    pinky_splay_cost: float = 0.2
    
    # thumb splay is different, the thumb has a lower and upper splay bound, and a rest position, the cost is calculated as deviation from the rest position
    thumb_down_splay_bound: float = 90
    """Maximum angle the thumb can splay down (towards the wrist), in degrees"""
    thumb_up_splay_bound: float = 20
    """Maximum angle the thumb can point up (away from the wrist), in degrees, 0 is pointing parallel to the forearm away from the wrist, positive numbers are underneath the palm"""
    thumb_rest_position: float = 45
    """Angle the thumb is rotated to when the hand is in a resting position, in degrees"""
    thumb_splay_cost: float = 0.25
    """Cost of splaying the thumb, in arbitrary units"""
    
    # finger contraction characteristics
    # for now, a simplified model is used, where the finger can contract to a % of its length, not very realistic, but it should work in most cases
    # each finger also has a default contraction, which is the % of its length it is contracted to when the hand is in a resting position
    # cost is calculated as (cost * deviation from default contraction) for each finger, for now
    
    index_max_contraction: float = 0.5
    """Maximum percentage of the index finger's length it can contract to"""
    index_default_contraction: float = 0.8
    """Default percentage of the index finger's length it uses when the hand is in a resting position (1 means no contraction, don't make it less than the max contraction)"""
    index_contraction_cost: float = 0.3
    """Cost of contracting the index finger, in arbitrary units"""
    middle_max_contraction: float = 0.55
    """Maximum percentage of the middle finger's length it can contract to"""
    middle_default_contraction: float = 0.8
    """Default percentage of the middle finger's length it uses when the hand is in a resting position (1 means no contraction, don't make it less than the max contraction)"""
    middle_contraction_cost: float = 0.38
    """Cost of contracting the middle finger, in arbitrary units"""
    ring_max_contraction: float = 0.6
    """Maximum percentage of the ring finger's length it can contract to"""
    ring_default_contraction: float = 0.8
    """Default percentage of the ring finger's length it uses when the hand is in a resting position (1 means no contraction, don't make it less than the max contraction)"""
    ring_contraction_cost: float = 0.43
    """Cost of contracting the ring finger, in arbitrary units"""
    pinky_max_contraction: float = 0.45
    """Maximum percentage of the pinky finger's length it can contract to"""
    pinky_default_contraction: float = 0.8
    """Default percentage of the pinky finger's length it uses when the hand is in a resting position (1 means no contraction, don't make it less than the max contraction)"""
    pinky_contraction_cost: float = 0.27
    """Cost of contracting the pinky finger, in arbitrary units"""
    thumb_max_contraction: float = 0.5 
    """Maximum percentage of the thumb's length it can contract to"""
    thumb_default_contraction: float = 0.8
    """Default percentage of the thumb's length it uses when the hand is in a resting position (1 means no contraction, don't make it less than the max contraction)"""
    thumb_contraction_cost: float = 0.2
    """Cost of contracting the thumb, in arbitrary units"""
    
    def __init__(self,  *args:tuple[Any,...], **kwargs:dict[str,Any]):
        """Initialize the hand shape, and assert that the values are valid"""
        super().__init__(*args, **kwargs)
        self._assert_integrity()
    
    def _assert_integrity(self):
        """Raise an assertionError if any of the values are invalid"""        
        for default_contraction, max_contraction in zip([self.index_default_contraction, self.middle_default_contraction, self.ring_default_contraction, self.pinky_default_contraction, self.thumb_default_contraction],
                                                        [self.index_max_contraction, self.middle_max_contraction, self.ring_max_contraction, self.pinky_max_contraction, self.thumb_max_contraction]):
            assert default_contraction <= max_contraction, "default contraction cannot be greater than max contraction"

@dataclass
class HandPosition:
    """holds the position/pose of a hand, default values are unnatural, this should be generated by a model
    """
    wrist_rotation: float = 0
    """wrist deviation in degrees from straight forward, positive is outwards, negative is inwards"""
    thumb_splay: float = 0
    """angle of the thumb relative to pointing straight ahead, positive is moving towards being perpendicular to the wrist
    ^ = 0  |  <- = 90 | -> = -90 """
    thumb_extension: float = 1
    """percentage of the thumb's length it is extended, 1 is fully extended, 0 is fully contracted (not possible in real life)"""
    index_splay: float = 0
    """angle of the index finger relative to pointing straight ahead, 0 = |, \\ = positive, negative not possible"""
    index_extension: float = 1
    """percentage of the index finger's length it is extended, 1 is fully extended, 0 is fully contracted (not possible in real life)"""
    middle_splay: float = 0
    """angle of the middle finger relative to pointing straight ahead, 0 = |, \\ = positive, negative not possible"""
    middle_extension: float = 1
    """percentage of the middle finger's length it is extended, 1 is fully extended, 0 is fully contracted (not possible in real life)"""
    ring_splay: float = 0
    """angle of the ring finger relative to pointing straight ahead, 0 = |, positive not possible, / = negative"""
    ring_extension: float = 1
    """percentage of the ring finger's length it is extended, 1 is fully extended, 0 is fully contracted (not possible in real life)"""
    pinky_splay: float = 0
    """angle of the pinky finger relative to pointing straight ahead, 0 = |, positive not possible, / = negative"""
    pinky_extension: float = 1
    """percentage of the pinky finger's length it is extended, 1 is fully extended, 0 is fully contracted (not possible in real life)"""
    
    def calculate_cost(self, hand_shape:HandShape) -> float:
        """Calcuates the cost of this hand position, based on the hand shape

        Args:
            hand_shape (HandShape): hand shape to calculate the cost for

        Returns:
            float: the cost of this hand position
        """
        total_cost = 0
        # first, make sure we aren't going out of bounds
        if self.wrist_rotation < -hand_shape.wrist_inwards_bound or \
                self.wrist_rotation > hand_shape.wrist_outwards_bound or \
                self.thumb_splay < -hand_shape.thumb_down_splay_bound or \
                self.thumb_splay > hand_shape.thumb_up_splay_bound or \
                self.index_splay < -hand_shape.index_max_splay or \
                self.index_splay > 0 or \
                self.middle_splay < -hand_shape.middle_max_splay or \
                self.middle_splay > 0 or \
                self.ring_splay < -hand_shape.ring_max_splay or \
                self.ring_splay > 0 or \
                self.pinky_splay < -hand_shape.pinky_max_splay or \
                self.pinky_splay > 0 or \
                self.thumb_extension < hand_shape.thumb_max_contraction or \
                self.thumb_extension > 1 or \
                self.index_extension < hand_shape.index_max_contraction or \
                self.index_extension > 1 or \
                self.middle_extension < hand_shape.middle_max_contraction or \
                self.middle_extension > 1 or \
                self.ring_extension < hand_shape.ring_max_contraction or \
                self.ring_extension > 1 or \
                self.pinky_extension < hand_shape.pinky_max_contraction or \
                self.pinky_extension > 1:
            return math.inf
        
        
        # wrist rotation
        deviation = abs(self.wrist_rotation - hand_shape.wrist_rest_position)
        if self.wrist_rotation < hand_shape.wrist_rest_position:
            total_cost += deviation * hand_shape.wrist_inwards_difficulty
        else:
            total_cost += deviation * hand_shape.wrist_outwards_difficulty
        # thumb splay and extension
        deviation = abs(self.thumb_splay - hand_shape.thumb_rest_position)
        total_cost += deviation * hand_shape.thumb_splay_cost
        deviation = abs(self.thumb_extension - hand_shape.thumb_default_contraction)
        total_cost += deviation * hand_shape.thumb_contraction_cost
        # index splay and extension
        deviation = abs(self.index_splay - hand_shape.index_max_splay)
        total_cost += deviation * hand_shape.index_splay_cost
        deviation = abs(self.index_extension - hand_shape.index_default_contraction)
        total_cost += deviation * hand_shape.index_contraction_cost
        # middle splay and extension
        deviation = abs(self.middle_splay - hand_shape.middle_max_splay)
        total_cost += deviation * hand_shape.middle_splay_cost
        deviation = abs(self.middle_extension - hand_shape.middle_default_contraction)
        total_cost += deviation * hand_shape.middle_contraction_cost
        # ring splay and extension
        deviation = abs(self.ring_splay - hand_shape.ring_max_splay)
        total_cost += deviation * hand_shape.ring_splay_cost
        deviation = abs(self.ring_extension - hand_shape.ring_default_contraction)
        total_cost += deviation * hand_shape.ring_contraction_cost
        # pinky splay and extension
        deviation = abs(self.pinky_splay - hand_shape.pinky_max_splay)
        total_cost += deviation * hand_shape.pinky_splay_cost
        deviation = abs(self.pinky_extension - hand_shape.pinky_default_contraction)
        total_cost += deviation * hand_shape.pinky_contraction_cost
        return total_cost
        
    
    

class Hands:
    """hand movement and difficulty estimation
    """
    def __init__(self, shape:HandShape):
        """Initialize the hands, and set the shape

        Args:
            shape (HandShape): shape of the hands, both are assumed to be the same shape
        """        """Initialize the hands, and set the shape"""
        self.left_shape = shape
        self.right_shape = shape
        
    def get_fingertip_coords(self, right_hand:bool ,pose:HandPosition) -> tuple[tuple[float,float], tuple[float,float], tuple[float,float], tuple[float,float], tuple[float,float]]:
        """Get the coordinates of the fingertips of a hand, **Still in hand coordinate space**, this means the coordinates are relative to the wrists centerpoint
        
        for both hands, after calculating this, you would need to translate the coordinates by where the hand is in the world

        Args:
            right_hand (bool): whether the hand is the right hand or not, false means left hand
            pose (HandPosition): position of the hand

        Returns:
            tuple[tuple[float,float], tuple[float,float], tuple[float,float], tuple[float,float], tuple[float,float]]: tuple of 5 tuples, each tuple is the (x,y) coordinates of a fingertip, in mm, relative to the wrist's centerpoint. The order is (thumb, index, middle, ring, pinky)
        """        
        # thumb first
        hand_shape = self.right_shape if right_hand else self.left_shape
        
        thumbpos:tuple[float,float] = hand_shape.thumb_root_position
        thumb_tip_offset_x = math.sin(math.radians(pose.thumb_splay)) * hand_shape.thumb_length * pose.thumb_extension
        thumb_tip_offset_y = math.cos(math.radians(pose.thumb_splay)) * hand_shape.thumb_length * pose.thumb_extension
        thumbpos = (thumbpos[0] + thumb_tip_offset_x, thumbpos[1] + thumb_tip_offset_y)
        
        indexpos:tuple[float,float] = hand_shape.index_root_position
        index_tip_offset_x = math.sin(math.radians(pose.index_splay)) * hand_shape.index_length * pose.index_extension
        index_tip_offset_y = math.cos(math.radians(pose.index_splay)) * hand_shape.index_length * pose.index_extension
        indexpos = (indexpos[0] + index_tip_offset_x, indexpos[1] + index_tip_offset_y)
        
        middlepos:tuple[float,float] = hand_shape.middle_root_position
        middle_tip_offset_x = math.sin(math.radians(pose.middle_splay)) * hand_shape.middle_length * pose.middle_extension
        middle_tip_offset_y = math.cos(math.radians(pose.middle_splay)) * hand_shape.middle_length * pose.middle_extension
        middlepos = (middlepos[0] + middle_tip_offset_x, middlepos[1] + middle_tip_offset_y)
        
        ringpos:tuple[float,float] = hand_shape.ring_root_position
        ring_tip_offset_x = math.sin(math.radians(pose.ring_splay)) * hand_shape.ring_length * pose.ring_extension
        ring_tip_offset_y = math.cos(math.radians(pose.ring_splay)) * hand_shape.ring_length * pose.ring_extension
        ringpos = (ringpos[0] + ring_tip_offset_x, ringpos[1] + ring_tip_offset_y)
        
        pinkypos:tuple[float,float] = hand_shape.pinky_root_position
        pinky_tip_offset_x = math.sin(math.radians(pose.pinky_splay)) * hand_shape.pinky_length * pose.pinky_extension
        pinky_tip_offset_y = math.cos(math.radians(pose.pinky_splay)) * hand_shape.pinky_length * pose.pinky_extension
        pinkypos = (pinkypos[0] + pinky_tip_offset_x, pinkypos[1] + pinky_tip_offset_y)
        
        # now apply wrist rotation
        to_return:list[tuple[float, float]] = []
        wrist_rotation_amount = pose.wrist_rotation
        for pos in (thumbpos, indexpos, middlepos, ringpos, pinkypos):
            x,y = pos
            # rotate about (0,0)
            x = x * math.cos(math.radians(wrist_rotation_amount)) - y * math.sin(math.radians(wrist_rotation_amount))
            y = x * math.sin(math.radians(wrist_rotation_amount)) + y * math.cos(math.radians(wrist_rotation_amount))
            x = x if right_hand else -x # flip x if left hand
            to_return.append((x,y))
            
        return tuple(to_return) # type: ignore # linter doesn't realize it's guaranteed to be a 5-tuple

        
