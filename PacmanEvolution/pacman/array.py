"""
This file contains code associated with representing an Array: a 2D grid of values.
"""

import functools
import itertools
import operator
from typing import Dict, Generic, List, Tuple, TypeVar, Union

from pacman.tech_util import flatten_2d, map_2d
from pacman.util import Vector

# an Array can contain values of variable type
ArrayType = TypeVar('ArrayType')


class Array(Generic[ArrayType]):
    """
    An Array is a 2D grid containing values of some type (represented by ArrayType).
    There are a number of ways to view and manipulate Arrays.
    The most useful is probably the ability to index an Array by a util.Vector.
    For example, given some Array `array` and Vector `vector`:
       array[vector]
    """

    def __init__(self, lst: List[List[ArrayType]]):
        self._array: List[List[ArrayType]] = [column.copy() for column in lst]
        self._cache_indicate: Dict[ArrayType, IndicatorArray] = {}
        self._cache_list: Dict[ArrayType, List[Vector]] = {}

    def indicate(self, value: ArrayType) -> 'IndicatorArray':
        """
        Create an IndicatorArray based on the given Array and value.
        This returns an array of booleans indicating whether each value
        in the Array is equal to the given value.
        """
        if value not in self._cache_indicate:
            self._cache_indicate[value] = IndicatorArray(self._array, value)
        return self._cache_indicate[value]

    def list(self, value: ArrayType) -> List[Vector]:
        """
        Return a list of locations in the Array at which
        the value is equal to the given value.
        """
        if value not in self._cache_list:
            result = []
            for x, y in itertools.product(*map(range, self.shape)):
                if self._array[x][y] == value:
                    result.append(Vector(x, y))
            self._cache_list[value] = result
        return self._cache_list[value]

    def contains(self, vector: Tuple) -> bool:
        """
        Whether the given location is inside the Array.:
        """
        return (0 <= vector[0] < len(self._array)) and (0 <= vector[1] < len(self._array[0]))

    @property
    def shape(self) -> Vector:
        """
        Get the shape of the Array.
        """
        if self._array:
            return Vector(len(self._array), len(self._array[0]))
        else:
            return Vector.zero

    @property
    def coords(self) -> List[Vector]:
        """
        A list of all coordinates that are within the Array.
        """
        return list(map(lambda t: Vector(*t), itertools.product(*map(range, self.shape))))

    @property
    def transpose(self) -> 'Array[ArrayType]':
        """
        Transpose the Array (common matrix operation).
        """
        return self.__class__(list(map(list, zip(*self._array))))

    @property
    def mirror_hor(self) -> 'Array[ArrayType]':
        """
        Mirror the Array horizontally.
        """
        return self.__class__(list(reversed(self._array)))

    @property
    def mirror_ver(self) -> 'Array[ArrayType]':
        """
        Mirror the Array vertically.
        """
        return self.transpose.mirror_hor.transpose

    def copy(self) -> 'Array[ArrayType]':
        """
        Create a copy of the array.
        """
        return Array([column.copy() for column in self._array])

    def __len__(self) -> int:
        return len(self._array)

    def __getitem__(self, item) -> Union[ArrayType, None]:
        if not isinstance(item, tuple) or not len(item) == 2:
            raise ValueError('can only index Array by 2-tuple (e.g. array[x,y])')
        if self.contains(item):
            x, y = item
            return self._array[x][y]
        return None

    def __setitem__(self, key, value):
        if not isinstance(key, tuple) or not len(key) == 2:
            raise ValueError('can only index Array by 2-tuple (e.g. array[x,y])')

        self._cache_indicate.clear()
        self._cache_list.clear()
        x, y = key
        self._array[x][y] = value

    def __repr__(self) -> str:
        max_len = max(map(len, map(str, flatten_2d(self._array))))
        space_sep = 1
        columns = []
        for column in self._array:
            cells = []
            for cell in column:
                cells.append(str(cell).center(max_len))
            columns.append((' ' * space_sep).join(cells))
        return '\n'.join(columns)

    def __bool__(self) -> bool:
        return any(map(any, self._array))

    def __eq__(self, other) -> bool:
        if isinstance(other, self.__class__):
            return self._array == other._array
        else:
            return False

    def __ne__(self, other) -> bool:
        return not self == other

    def __hash__(self) -> int:
        column_hashes = map(hash, map(tuple, self._array))
        return functools.reduce(operator.xor, column_hashes)


class IndicatorArray(Array[bool]):
    """
    An array consisting only of booleans, created by an Array to indicate
    whether the values in that array are equal to some given value.
    """

    def __init__(self, lst: List[List[ArrayType]], value: ArrayType):
        self._lst = lst
        self._value = value
        super().__init__(self._full_indicators())

    def list(self, value: bool = None) -> List[Vector]:
        """
        Return a list of locations in the Array at which
        the value is equal to the given value.
        """
        if value is None:
            return super().list(True)
        else:
            return super().list(value)

    @property
    def transpose(self) -> 'IndicatorArray':
        """
        Transpose the Array (common matrix operation).
        """
        return self.__class__(list(map(list, zip(*self._lst))), self._value)

    @property
    def mirror_hor(self) -> 'IndicatorArray':
        """
        Mirror the Array horizontally.
        """
        return self.__class__(list(reversed(self._lst)), self._value)

    @property
    def mirror_ver(self) -> 'IndicatorArray':
        """
        Mirror the Array vertically.
        """
        return self.transpose.mirror_hor.transpose

    def copy(self) -> 'IndicatorArray':
        """
        Create a copy of the array.
        """
        return IndicatorArray([column.copy() for column in self._lst], self._value)

    def _full_indicators(self) -> List[List[bool]]:
        return map_2d(lambda v: v == self._value, self._lst)

    def __len__(self) -> int:
        return len(self.list())

    def __getitem__(self, item) -> bool:
        return super().__getitem__(item)

    def __setitem__(self, key, value):
        raise ValueError('cannot assign to readonly indicator array')

    def __repr__(self) -> str:
        indicators = self._full_indicators()
        max_len = max(map(len, map(str, flatten_2d(indicators))))
        space_sep = 1
        columns = []
        for column in indicators:
            cells = []
            for cell in column:
                cells.append(str(cell).center(max_len))
            columns.append((' ' * space_sep).join(cells))
        return '\n'.join(columns)

    def __bool__(self) -> bool:
        return bool(self.list())

    def __eq__(self, other) -> bool:
        if isinstance(other, self.__class__):
            return self._value == other._value and self._lst == other._lst
        else:
            return False

    def __ne__(self, other) -> bool:
        return not self == other

    def __hash__(self) -> int:
        return hash(self._value) ^ hash(self._lst)
