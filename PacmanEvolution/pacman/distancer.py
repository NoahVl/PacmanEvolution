"""
This file contains a distance calculator to use during contests
to find real distances between points in the maze,
rather than heuristics like the Manhattan distance.
"""

import collections
import queue
from . import util


class Distancer:
    """
    A distance calculator to use during contests
    to find real distances between points in the maze,
    rather than heuristics like the Manhattan distance.
    """

    def __init__(self, gstate):
        self.walls = gstate.walls
        self.distances = collections.defaultdict(lambda: float('inf'))

    def precompute_distances(self):
        """
        Call this before the Pacman round starts to calculate
        all maze distances between all pairs of points.
        """
        all_points = self.walls.list(False)

        for starting_position in all_points:
            frontier = queue.PriorityQueue(len(all_points))
            frontier.put((0, starting_position))
            visited = set()

            while not frontier.empty():
                dist, position = frontier.get()
                if position in visited:
                    continue
                self.distances[starting_position, position] = dist
                visited.add(position)

                for move in util.Move.no_stop:
                    new_position = position + move.vector
                    if not self.walls[new_position] and new_position not in visited:
                        frontier.put((dist+1, new_position))

    def get_distance(self, pos1, pos2):
        """
        Gets the real maze distance between the two points.
        If there is no path between the points (e.g., one is a wall)
        this will return infinity.
        """
        return self.distances[pos1, pos2]
