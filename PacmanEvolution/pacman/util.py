"""
This file contains utility functions and classes which are
only barely related to Pacman. Even less strongly related
code is found in tech_util.py.
"""

import enum
import math
import numbers
import queue
from typing import List, NamedTuple, Tuple

from pacman.tech_util import classproperty


class PriorityFunctionQueue(queue.PriorityQueue):
    """
    A queue based on the classes in the standard library `queue` module,
    which uses a given function to determine the priority of each given item.
    For example:
      queue = PriorityFunctionQueue(some_function)
      queue.put(an_element)
      the_element = queue.get()
    """

    def __init__(self, priority_fn=lambda x: 0):
        super().__init__()
        self.priority_fn = priority_fn
        self.mapping = {}
        self.next_id = 0

    def put(self, item, *args, **kwargs):
        priority = self.priority_fn(item)
        self.mapping[self.next_id] = item
        super().put((priority, self.next_id), *args, **kwargs)
        self.next_id += 1

    def get(self, *args, **kwargs):
        _, ident = super().get(*args, **kwargs)
        return self.mapping[ident]


class Vector(NamedTuple('Vector', [('x', int), ('y', int)])):
    """
    A 2D vector, representing a position or movement in 2D space.
    """

    # noinspection PyMethodParameters
    @classproperty
    def zero(cls) -> 'Vector':
        """
        The zero vector.
        """
        return Vector(0, 0)

    # noinspection PyMethodParameters
    @classproperty
    def unit(cls) -> 'Vector':
        """
        The unit vector.
        """
        return Vector(1, 1)

    def __add__(self, other) -> 'Vector':
        if isinstance(other, Vector):
            return Vector(self.x + other.x, self.y + other.y)
        elif isinstance(other, numbers.Number):
            return Vector(self.x + other, self.y + other)
        else:
            return super().__add__(other)

    def __sub__(self, other) -> 'Vector':
        if isinstance(other, Vector):
            return Vector(self.x - other.x, self.y - other.y)
        elif isinstance(other, numbers.Number):
            return Vector(self.x - other, self.y - other)
        else:
            return super().__sub__(other)

    def __mul__(self, other) -> 'Vector':
        if isinstance(other, Vector):
            return Vector(self.x * other.x, self.y * other.y)
        elif isinstance(other, numbers.Number):
            return Vector(self.x * other, self.y * other)
        else:
            return super().__mul__(other)

    def __rmul__(self, other) -> 'Vector':
        return self.__mul__(other)

    def __truediv__(self, other: numbers.Number) -> 'Vector':
        if isinstance(other, Vector):
            return Vector(self.x / other.x, self.y / other.y)
        elif isinstance(other, numbers.Number):
            return Vector(self.x / other, self.y / other)
        else:
            return super().__truediv__(other)

    def __floordiv__(self, other) -> 'Vector':
        if isinstance(other, Vector):
            return Vector(self.x // other.x, self.y // other.y)
        elif isinstance(other, numbers.Number):
            return Vector(self.x // other, self.y // other)
        else:
            return super().__floordiv__(other)

    def __abs__(self) -> 'Vector':
        return Vector(abs(self.x), abs(self.y))

    def __pow__(self, power, modulo=None):
        if isinstance(power, numbers.Number):
            return Vector(pow(self.x, power, modulo), pow(self.y, power, modulo))
        else:
            super().__pow__(power, modulo)


class Move(enum.Enum):
    """
    An enumeration of types representing standard movements in the Pacman world.
    """
    up = Vector(0, 1)
    down = Vector(0, -1)
    right = Vector(1, 0)
    left = Vector(-1, 0)
    stop = Vector(0, 0)

    @property
    def vector(self) -> Vector:
        """
        The vector describing the movement.
        """
        return self.value

    @property
    def opposite(self) -> 'Move':
        """
        The opposite of the given movement.
        """
        if self == Move.stop:
            return Move.stop
        else:
            return Move.by_index(self.index + 1 - 2 * (self.index % 2))

    @property
    def degrees(self) -> float:
        """
        The movement vector converted to degrees.
        """
        return 180 / math.pi * math.atan2(self.vector.y, self.vector.x)

    @property
    def index(self) -> int:
        """
        The index of the movement as defined in the enumeration.
        """
        # noinspection PyTypeChecker
        return list(Move).index(self)

    @classmethod
    def by_index(cls, i) -> 'Move':
        """
        Get a Move by index as defined in the enumeration.
        """
        # noinspection PyTypeChecker
        return list(cls)[i]

    # noinspection PyMethodParameters
    @classproperty
    def no_stop(cls) -> List['Move']:
        """
        Get all moves except stop.
        """
        # noinspection PyTypeChecker
        return [move for move in cls if move != cls.stop]
    
    def __lt__(self, other):
        """
        Comparing two Moves: is self < other true? Required to sort Moves
        """
        if isinstance(other, Move):
            return self.value < other.value
        else:
            return NotImplemented


def manhattan(vector1: Vector, vector2: Vector) -> int:
    """
    The manhattan distance between the two vectors.
    """
    return sum(abs(vector1 - vector2))


def euclidean(vector1: Vector, vector2: Vector) -> float:
    """
    The euclidean distance between the two vectors.
    """
    return math.sqrt(sum((vector1 - vector2) ** 2))


# a (probability) distribution consists of values and associated weights
Distribution = Tuple[List[Move], List[float]]
