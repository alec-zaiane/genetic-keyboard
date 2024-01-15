"""Key and Keyboard classes, for representing keys and keyboards physically."""
from __future__ import annotations
from typing import Optional
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    import pygame

class Key:
    """Physical key on a keyboard."""
    def __init__(self, letter: str, x: float, y: float, width: float, height: float):
        """Create a new key, position is relative to the top left corner of the keyboard.

        Args:
            letter (str): the letter on the key (must be one character)
            x (int): x position of the key (mm) (top left corner)
            y (int): y position of the key (mm) (top left corner)
            width (int): width of the key (mm)
            height (int): height of the key (mm)
        """        
        assert len(letter) == 1
        self.letter = letter
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.pressed = False
        
    def check_position(self, x:float, y:float) -> bool:
        """Check whether position (x, y) is on this key.

        Args:
            x (float): x position in mmm relative to top left corner of keyboard
            y (float): y position in mmm relative to top left corner of keyboard

        Returns:
            bool: whether (x, y) is on this key
        """
        if x < self.x or x > self.x + self.width or y < self.y or y > self.y + self.height:
            return False
        return True
    
    def intersecting(self, other:Key) -> bool:
        """Check if this key is intersecting another key.

        Args:
            other (Key): The other key to check against.

        Returns:
            bool: Whether the two keys are intersecting.
        """
        if self.x + self.width < other.x or \
            self.x > other.x + other.width or \
            self.y + self.height < other.y or \
            self.y > other.y + other.height:
            return False
        return True
    
    def __hash__(self):
        return hash((self.x, self.y, self.width, self.height))
    
    def __str__(self):
        return f"Key {self.letter} @ ({self.x}, {self.y}) [{self.width} by {self.height}]"
    
class Keyboard:
    """Physical keyboard."""
    def __init__(self, keys: list[Key]):
        """Create a new keyboard.

        Args:
            keys (list[Key]): list of keys on the keyboard.
        Raises:
            ValueError: If any of the keys are intersecting.
            ValueError: if there are more than 3 keys with the same letter
        """
        self.keys = keys
        possible_intersections = set(keys)
        while possible_intersections:
            key = possible_intersections.pop()
            for other in possible_intersections:
                if key.intersecting(other):
                    raise ValueError(f"Keys {key} and {other} are intersecting")
        self.key_map:dict[str, tuple[Optional[Key],Optional[Key],Optional[Key]]] = {}
        """key_map maps letters to a tuple of keys that have that letter."""
        # build a cache now so we don't have to search through all the keys every time
        for key in keys:
            if key.letter not in self.key_map:
                self.key_map[key.letter] = (key, None, None)
            elif self.key_map[key.letter][1] is None:
                self.key_map[key.letter] = (self.key_map[key.letter][0], key, None)
            elif self.key_map[key.letter][2] is None:
                self.key_map[key.letter] = (self.key_map[key.letter][0], self.key_map[key.letter][1], key)
            else:
                raise ValueError(f"More than 3 keys with letter {key.letter}")
        
        
    def key_at(self, x:float, y:float) -> Optional[Key]:
        """Get the key at position (x, y).

        Args:
            x (float): x position in mm
            y (float): y position in mm

        Returns:
            Optional[Key]: The key at position (x, y), or None if there is no key there.
        """        
        for key in self.keys:
            if key.check_position(x, y):
                return key
        return None # no key at that position
    
    def find_letter(self, letter:str) -> tuple[Optional[Key], Optional[Key], Optional[Key]]:
        """Find a letter on the keyboard.

        Args:
            letter (str): The letter to find.

        Returns:
            tuple[Optional[Key], Optional[Key], Optional[Key]]: tuple of 3 entries, each entry is either None or a key with that letter.
        """
        return self.key_map.get(letter, (None, None, None))
    
    def render_to_surface(self, padding:int=5, scale:float=2.5) -> pygame.Surface:
        """Render the keyboard to a pygame surface.
        
        Args:
            padding (int, optional): Padding around the keyboard in mm. Defaults to 5mm.
            scale(float, optional): Scale to render at, each mm will be `scale` pixels. Defaults to 5.

        Returns:
            pygame.Surface: The keyboard rendered to a surface.
        """
        import pygame
        min_x = min(key.x for key in self.keys)
        min_y = min(key.y for key in self.keys)
        max_x = max(key.x + key.width for key in self.keys)
        max_y = max(key.y + key.height for key in self.keys)
        width = int((max_x - min_x + 2*padding)*scale)
        height = int((max_y - min_y + 2*padding)*scale)
        surface = pygame.Surface((width, height))
        surface.fill((0,0,0))
        for key in self.keys:
            # find the top left corner of the key in screen space
            x = int((key.x - min_x + padding)*scale)
            y = int((key.y - min_y + padding)*scale)
            # find the width and height of the key in screen space
            width = int(key.width*scale)
            height = int(key.height*scale)
            # draw the key
            col = (0, 255, 0) if key.pressed else (128,128,128)
            surface.fill(col, rect=(x, y, width, height))
            # draw the letter
            font = pygame.font.SysFont("arial", int(10*scale))
            text = font.render(key.letter, True, (0,0,0))
            text_rect = text.get_rect(center=(x+width/2, y+height/2))
            surface.blit(text, text_rect)
        return surface
        
        
    
def generate_qwerty() -> Keyboard:
    """Generate a QWERTY keyboard, used mainly for testing.

    Returns:
        Keyboard: QWERTY keyboard.
    """
    rows = ["1234567890-=", "qwertyuiop[]", "asdfghjkl;'", "zxcvbnm,./"]
    keys:list[Key] = []
    for i, row in enumerate(rows):
        for j, letter in enumerate(row):
            # key dimensions are width: 19.05mm, height: 19.05mm, spacing between keys: 3.175mm
            # each row adds 22.225mm to the height, and an indent of 9.525mm
            keys.append(Key(letter,
                            x=(i*9.525)+(j*22.225),
                            y=(i*22.225),
                            width=19.05,
                            height=19.05))
            
    # now add the spacebar
    keys.append(Key(" ", x=3*22.225, y=len(rows)*22.225, width=114.3, height=19.05))
    return Keyboard(keys)