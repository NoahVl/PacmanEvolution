"""
This file contains classes for creating different kinds of displays for the Pacman game.
"""

import abc
import itertools
import math
import numbers
import sys
import tkinter
from typing import List, Tuple

from . import array, gamestate, tech_util, util


class Display(abc.ABC):
    """
    An abstract display class, defining the interface for displays in general.
    """

    def __init__(self, scale: numbers.Number):
        self.scale = scale

    def initialise(self, gstate: gamestate.Gamestate, cell_values: array.Array[numbers.Number]):
        """
        Pass initialisation data to the display, including the cell values that are constant throughout the game.
        """
        pass

    @property
    def preferred_timedelta(self) -> float:
        """
        The time that this display would prefer to sleep in-between displaying consecutive gamestates.
        """
        return 0

    @abc.abstractmethod
    def show(self, gstate: gamestate.Gamestate):
        """
        Display the given gamestate.
        """
        pass

    @abc.abstractmethod
    def get_keypress(self) -> str:
        """
        Get input from the user of the display.
        """
        pass

    def reset(self):
        """
        Resets the display.
        """
        pass


class NoDisplay(Display):
    """
    Do not display anything.
    """

    def show(self, gstate: gamestate.Gamestate):
        """
        Display the given gamestate.
        """
        pass

    def get_keypress(self):
        """
        Get input from the user of the display.
        """
        return None


class TerminalDisplay(Display):
    """
    Display the game in the terminal.
    """

    def show(self, gstate: gamestate.Gamestate):
        """
        Display the given gamestate.
        """
        print('-' * (gstate.shape.x * 2 - 1))
        print(gstate)

    @property
    def preferred_timedelta(self) -> float:
        """
        The time that this display would prefer to sleep in-between displaying consecutive gamestates.
        """
        return 0.05

    def get_keypress(self) -> str:
        """
        Get input from the user of the display.
        """
        return tech_util.getsym()


class GraphicalDisplay(Display):
    """
    Display a graphical representation of the game in a window.
    """

    WINDOW_TITLE = 'Pacman'
    TILE_SIZE = property(lambda self: 30 * self.scale)  # the size of each grid tile
    INFO_PANE_HEIGHT = 1.17  # the height of the ścore' pane below the game

    BACKGROUND_COLOR = 'black'
    PACMAN_COLOR = 'yellow'
    DOT_COLOR = 'white'
    PELLET_COLOR = 'white'
    WALL_COLOR = 'blue'
    GHOST_COLORS = [(0, .3, .9), (.98, .41, .07), (.1, .75, .7), (1, 0.6, 0)]  # RGB values
    SCARED_COLOR = (1, 1, 1)
    GHOST_EYE_COLOR = 'white'
    GHOST_PUPIL_COLOR = 'black'
    SCORE_TEXT_COLOR = 'yellow'

    PACMAN_RADIUS = 0.5
    GHOST_SIZE = 0.65
    DOT_RADIUS = 0.1
    PELLET_RADIUS = 0.25
    WALL_RADIUS = 0.15
    WALL_LINE_WIDTH = 0.067
    CELL_SIZE = 1
    FONT_SIZE = 0.8

    NON_STATIC_TAG = 'non-static'  # used for marking which elements need to be redrawn with each move

    # list containing vectors pointing towards the four unit corners, used in graphisc calculations
    QUADRANTS = [util.Vector(-1, -1), util.Vector(-1, 1), util.Vector(1, 1), util.Vector(1, -1)]

    # the outline shape of a ghost
    GHOST_SHAPE = [util.Vector(0, 0.3),
                   util.Vector(0.25, 0.75),
                   util.Vector(0.5, 0.3),
                   util.Vector(0.75, 0.75),
                   util.Vector(0.75, -0.5),
                   util.Vector(0.5, -0.75),
                   util.Vector(-0.5, -0.75),
                   util.Vector(-0.75, -0.5),
                   util.Vector(-0.75, 0.75),
                   util.Vector(-0.5, 0.3),
                   util.Vector(-0.25, 0.75)]

    def __init__(self, scale: numbers.Number):
        super().__init__(scale)
        # declaration of some variables to satisfy type checker
        self._window: tkinter.Tk = None
        self.canvas: tkinter.Canvas = None
        self.mapshape: util.Vector = None
        self._current_keypress = None

    def initialise(self, gstate: gamestate.Gamestate, cell_values: array.Array[numbers.Number]):
        """
        Pass initialisation data to the display, including the cell values that are constant throughout the game.
        """
        # calculate window size
        self.mapshape = gstate.shape
        width, height = self.mapshape.x * self.TILE_SIZE, (self.mapshape.y + self.INFO_PANE_HEIGHT) * self.TILE_SIZE

        # create window
        self._window = tkinter.Tk()
        self._window.protocol('WM_DELETE_WINDOW', lambda event: sys.exit(0))
        self._window.title(self.WINDOW_TITLE)
        self._window.resizable(0, 0)

        # setup input system
        self._window.focus_set()
        self._window.bind('<KeyPress>', self._key_press)
        self._current_keypress = None

        # create drawing canvas
        self.canvas = tkinter.Canvas(self._window, width=width, height=height, highlightthickness=0)
        self.canvas.pack()
        self.canvas.configure(background=self.BACKGROUND_COLOR)

        # draw static graphics (walls and cell values)
        self.draw_walls(gstate.walls.mirror_ver)
        if cell_values:
            self.draw_cell_values(cell_values.mirror_ver)

    @property
    def preferred_timedelta(self) -> float:
        """
        The time that this display would prefer to sleep in-between displaying consecutive gamestates.
        """
        return 0.1

    def show(self, gstate: gamestate.Gamestate):
        """
        Display the given gamestate.
        """
        self.canvas.delete(self.NON_STATIC_TAG)  # erase non-static graphics from previous turn
        self.draw_dots(gstate.dots.mirror_ver, self.DOT_RADIUS, self.DOT_COLOR)  # draw dots
        self.draw_dots(gstate.pellets.mirror_ver, self.PELLET_RADIUS, self.PELLET_COLOR)  # draw pellets
        # draw pacman
        if gstate.pacman:
            self.draw_pacman(self.flipud(gstate.pacman), gstate.facings[gstate.PACMAN_ID])
        # draw each ghost
        for ghost, timer, facing, color in zip(gstate.ghosts, gstate.timers, gstate.facings[1:], self.GHOST_COLORS):
            if ghost:
                self.draw_ghost(self.flipud(ghost), timer, facing, color)
        self.draw_score(gstate.score)  # draw score text
        # propagate changes to screen
        self.canvas.update_idletasks()
        self.canvas.update()

    def _key_press(self, event):
        """
        Called when the user presses a key.
        """
        self._current_keypress = event.keysym  # save keypress

    def get_keypress(self) -> str:
        """
        Get input from the user of the display.
        """
        while self._current_keypress is None:  # wait for user input
            self.canvas.update()
        k, self._current_keypress = self._current_keypress, None  # move input to variable and clear input
        return k  # return input

    def flipud(self, vector: util.Vector):
        """
        Flip a location in the y direction.
        Used because the game's origin is bottom left while the screen's origin is top right.
        """
        return util.Vector(vector.x, self.mapshape.y - vector.y - 1)

    def draw_walls(self, walls: array.IndicatorArray):
        """
        Draw the walls of the layout.
        """
        for tile, quadrant in itertools.product(walls.coords, self.QUADRANTS):
            if walls[tile]:
                self._draw_wall_quadrant(walls, tile, quadrant)

    def _draw_wall_quadrant(self, walls: array.IndicatorArray, tile: util.Vector, quadrant: util.Vector):
        """
        Draw a single wall quadrant. This is a quarter of a tile.
        """
        tile_center = self.TILE_SIZE * (tile + 0.5)
        bases = [util.Vector(quadrant.x, 0), util.Vector(0, quadrant.y)]
        neighbors = [tile + base for base in bases]
        neighbor_walls = [walls[neighbor] for neighbor in neighbors]
        diagonal_wall = walls[tile + quadrant]

        # don't draw walls if the quadrant is surrounded by walls.
        if all(neighbor_walls) and diagonal_wall:
            return

        self._draw_wall_quadrant_center(bases, neighbor_walls, quadrant, tile_center)
        self._draw_wall_quadrant_sides(bases, neighbor_walls, tile_center)

    def _draw_wall_quadrant_center(self, bases: List[util.Vector], neighbor_walls: List[bool], quadrant: util.Vector,
                                   tile_center: util.Vector):
        """
        Draw the walls on the part of a tile quadrant that is at the center of the tile.
        """
        wall_size = self.WALL_RADIUS * self.TILE_SIZE
        if all(neighbor_walls):  # walls on both sides of the quadrant
            box_start = tile_center + wall_size * quadrant
            box_end = tile_center + 3 * wall_size * quadrant
            start = (270 + self.QUADRANTS.index(quadrant) * 90) % 360
            self._draw_wall_arc(box_start, box_end, start)
        elif any(neighbor_walls):  # wall on one side of the quadrant
            base0, base1 = (bases, reversed(bases))[neighbor_walls.index(True)]
            line_start = tile_center + 2 * wall_size * base0 + wall_size * base1
            line_end = tile_center + wall_size * base1
            self._draw_wall_line(line_start, line_end)
        else:  # wall on neither of the sides of the quadrant
            box_start = tile_center - wall_size * quadrant
            box_end = tile_center + wall_size * quadrant
            start = 90 + self.QUADRANTS.index(quadrant) * 90
            self._draw_wall_arc(box_start, box_end, start)

    def _draw_wall_quadrant_sides(self, bases: List[util.Vector], neighbor_walls: List[bool], tile_center: util.Vector):
        """
        Draw the walls on the part of a tile quadrant that are at the sides.
        """
        wall_size = self.WALL_RADIUS * self.TILE_SIZE
        # draw each side
        for neighbor_wall, base0, base1 in zip(neighbor_walls, bases, reversed(bases)):
            if neighbor_wall:
                line_start = tile_center + 2 * wall_size * base0 + wall_size * base1
                line_end = tile_center + 0.5 * self.TILE_SIZE * base0 + wall_size * base1
                self._draw_wall_line(line_start, line_end)

    def _draw_wall_line(self, line_start: util.Vector, line_end: util.Vector):
        """
        Draw a straight section of wall.
        """
        self.canvas.create_line(line_start, line_end, width=self.WALL_LINE_WIDTH * self.TILE_SIZE,
                                capstyle=tkinter.PROJECTING, fill=self.WALL_COLOR)

    def _draw_wall_arc(self, point0: util.Vector, point1: util.Vector, start: float):
        """
        Draw an arced section of wall.
        """
        points = point0, point1
        x0, x1 = sorted(point.x for point in points)
        y0, y1 = sorted(point.y for point in points)
        self.canvas.create_arc(x0, y0, x1 - 1, y1 - 1, start=start, extent=90,
                               width=self.WALL_LINE_WIDTH * self.TILE_SIZE, style=tkinter.ARC, outline=self.WALL_COLOR)

    def draw_cell_values(self, values: array.Array[numbers.Number]):
        """
        Draw cell values onto the grid (e.g. expansion order when using search).
        """
        cell_values = {vector: values[vector] for vector in values.coords if values[vector] is not None}
        max_value = max(cell_values.values()) if cell_values else None
        if max_value != 0:
            for cell, value in cell_values.items():
                corners = [self.TILE_SIZE * (cell + 0.5 + quadrant * self.CELL_SIZE * 0.5) for quadrant in
                           self.QUADRANTS]  # define the squares that will be drawn
                color = self.color((1 - value / max_value) * 0.5 + 0.25, 0.25, 0.25)
                self.canvas.create_polygon(*tech_util.flatten_2d(corners), fill=color)

    def draw_dots(self, dots: array.IndicatorArray, radius: float, color: str):
        """
        Draw dots of a certain size based on an indicator array.
        """
        for dot in dots.list():
            box_start = (dot + 0.5 - radius) * self.TILE_SIZE
            box_end = (dot + 0.5 + radius) * self.TILE_SIZE
            self.canvas.create_oval(*tuple(box_start), *tuple(box_end - 1), outline=color, fill=color,
                                    tag=self.NON_STATIC_TAG)

    def draw_pacman(self, pacpos: util.Vector, facing: util.Move):
        """
        Draw Pacman onto the grid.
        """
        box_start = (pacpos + 0.5 - self.PACMAN_RADIUS) * self.TILE_SIZE
        box_end = (pacpos + 0.5 + self.PACMAN_RADIUS) * self.TILE_SIZE
        mouth_angle = 75 + 40 * math.sin(math.pi * sum(pacpos))
        mouth_edge = facing.degrees + mouth_angle / 2
        self.canvas.create_arc(*tuple(box_start), *tuple(box_end - 1), outline=self.PACMAN_COLOR,
                               fill=self.PACMAN_COLOR, start=mouth_edge, extent=360 - mouth_angle,
                               tag=self.NON_STATIC_TAG)

    def draw_ghost(self, ghost: util.Vector, timer: int, facing: util.Move, color: Tuple[float, float, float]):
        """
        Draw a ghost onto the grid.
        """
        shape_coords = [(ghost + 0.5 + coord * self.GHOST_SIZE) * self.TILE_SIZE for coord in self.GHOST_SHAPE]
        if timer:
            color = self.SCARED_COLOR
        self.canvas.create_polygon(*tech_util.flatten_2d(shape_coords), fill=self.color(*color), smooth=True,
                                   tag=self.NON_STATIC_TAG)
        ghost_center = (ghost + 0.5) * self.TILE_SIZE
        sides = [util.Vector(-0.3, 0), util.Vector(0.3, 0)]
        height = util.Vector(0, -0.3)
        eyes = [side + height for side in sides]
        turning = 0.2 * facing.vector * util.Vector(1, -1)
        for eye in eyes:
            for turn_mult, size, part_color in zip([0.7, 1], [0.2, 0.1],
                                                   [self.GHOST_EYE_COLOR, self.GHOST_PUPIL_COLOR]):
                box_start = ghost_center + (eye + turning * turn_mult - size) * self.TILE_SIZE * self.GHOST_SIZE
                box_end = ghost_center + (eye + turning * turn_mult + size) * self.TILE_SIZE * self.GHOST_SIZE
                self.canvas.create_oval(*tuple(box_start), *tuple(box_end), fill=part_color, outline=part_color,
                                        tag=self.NON_STATIC_TAG)

    def draw_score(self, score: int):
        """
        Draw the score text onto the info pane.
        """
        text = f'SCORE: {score}'
        font = ('Helvetica', str(int(round(self.FONT_SIZE * self.TILE_SIZE))), 'bold')
        self.canvas.create_text(int(round(self.TILE_SIZE / 3)), self.mapshape.y * self.TILE_SIZE, text=text,
                                fill=self.SCORE_TEXT_COLOR,
                                anchor='nw', font=font, tag=self.NON_STATIC_TAG)

    @staticmethod
    def color(r, g, b):
        """
        Convert RGB values into a color string (used by tkinter).
        """
        return '#{:02x}{:02x}{:02x}'.format(int(r * 255), int(g * 255), int(b * 255))

    def reset(self):
        self._window.destroy()
