"""
This file contains code for representing elements of a Pacman level layout and loading a layout from a file.
"""

import enum
import itertools
import os
from typing import List, Optional, Tuple, Type

from . import agents, array, tech_util, util

LAYOUT_DIR = 'pacman/layout_files'
LAYOUT_SUFFIX = '.lay'


class LayoutObject(enum.Enum):
    """
    An enumeration of types representing objects in a Pacman layout.
    """
    empty = ' '
    wall = '%'
    pacman = 'P'
    ghost = 'G'
    ghost_scared = 'S'
    dot = '.'
    pellet = 'o'

    @classmethod
    def from_symbol(cls, symbol: str) -> 'LayoutObject':
        """
        Convert a string from a layout file to a LayoutObject.
        """
        switch = {str(obj): obj for obj in cls}
        for i in range(3):  # recognize different ghost types
            switch[str(i+1)] = LayoutObject.ghost
        if symbol not in switch:
            raise ValueError(f"unknown layout symbol '{symbol}'")
        return switch[symbol]

    def __str__(self) -> str:
        return self.value


class GhostType(enum.Enum):
    """
    An enumeration of types representing ghost types found in a Pacman layout.
    """
    no_ghost = 0
    track_ghost = 1    # 1
    random_ghost = 2   # or G
    chasing_ghost = 3  # 3

    @classmethod
    def from_symbol(cls, symbol: str) -> 'GhostType':
        if symbol == '1':
            return GhostType.track_ghost
        elif symbol == '2' or symbol == 'G':
            return GhostType.random_ghost
        elif symbol == '3':
            return GhostType.chasing_ghost
        else:
            return GhostType.no_ghost

    @property
    def agent(self) -> Optional[Type['Agent']]:
        if self == GhostType.no_ghost:
            return None
        elif self == GhostType.track_ghost:
            return agents.TrackGhostAgent
        elif self == GhostType.random_ghost:
            return agents.RandomGhostAgent
        elif self == GhostType.chasing_ghost:
            return agents.ChasingGhostAgent


def load_layout(filename: str) -> Tuple[array.Array, List[Tuple[GhostType, util.Vector]]]:
    """
    Given the name of a layout file, load and return the layout as an Array.
    Furthermore, load the specific ghost types as a list of (ghostType, position) tuples.
    """
    filepath = os.path.join(LAYOUT_DIR, filename + LAYOUT_SUFFIX)
    with open(filepath) as f:
        symbols = [list(line.strip()) for line in f]
    objects = tech_util.map_2d(LayoutObject.from_symbol, symbols)
    ghost_types = tech_util.map_2d(GhostType.from_symbol, symbols)

    ghosts = []
    shape = len(ghost_types), len(ghost_types[0])
    for x, y in itertools.product(*map(range, shape)):
        if ghost_types[x][y] != GhostType.no_ghost:
            ghost_position = util.Vector(y, shape[0] - x - 1)  # see comment below
            ghosts.append((ghost_types[x][y], ghost_position))

    # The display has its origin in the top right, but we are using
    # (1,1) as origin, so we transpose and mirror vertically.
    # Thus, we have to do the same to the ghost positions above.
    # To keep ghost order the same for the -g option, we sort
    # the ghosts based on the correct (transposed mirrored) position.
    ghosts = sorted(ghosts, key=lambda gh: gh[1])
    return array.Array(objects).transpose.mirror_ver, ghosts
