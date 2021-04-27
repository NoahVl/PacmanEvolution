"""
This file contains classes and functions that are used by the SearchAgent (see agents.py).
"""

import abc
import sys
from typing import Any, Callable, FrozenSet, Generic, List, NamedTuple, Tuple, TypeVar

from . import array, gamestate, util

# A search space consists of states which are of a certain type.
# This variable represents a generic state type for a search space
StateType = TypeVar('StateType')

# When transitions (moves) are applied to states in a search space,
# the new states that are reached are called successors.
# A Successor is a tuple that contains the successor state, a list of moves 
# that was used to transition to it, and the cost of making this transition
Successor = Tuple[StateType, List[util.Move], float]

"""
Search representations
"""


class SearchRepresentation(abc.ABC, Generic[StateType]):
    """
    A SearchRepresentation defines a search space.
    It does so by defining the start state,
    the goal test, and the successor function.
    In addition the representation can calculate the
    path cost of a path through the space.

    A SearchRepresentation uses a StateType
    the definition of its methods, which
    is simply the type of the states in the search space.

    A search representation also keeps track of
    the expansion order of states, which are used
    later by SearchAgent for its cell values.
    """

    def __init__(self, gstate: gamestate.Gamestate):
        self.expansion_count = 0
        self.expansion_order = array.Array([[None] * gstate.shape.y for _ in range(gstate.shape.x)])

    @property
    @abc.abstractmethod
    def start(self) -> StateType:
        """
        The initial state of the representation,
        from which searching begins.
        """
        pass

    def is_goal(self, state: StateType) -> bool:
        """
        Whether the given state is a goal state in this representations.
        The first line should be `super().is_goal(pacpos)`,
        where `pacpos` is the position of pacman in the given state,
        in order for SearchAgents's cell values to function.
        """
        self.expansion_order[state] = self.expansion_count
        self.expansion_count += 1
        return False

    @abc.abstractmethod
    def successors(self, state: StateType) -> List[Successor[StateType]]:
        """
        Get all successor states of the given state in this representation.
        """
        pass

    @abc.abstractmethod
    def pathcost(self, path: List[util.Move]) -> float:
        """
        Get the path cost of the given list of moves (executed from the start state).
        """
        pass


# A path cost function is a function used to compute the cost of a path
# In this course, we only use cost functions assigning a cost to the state (position) we land on after every move
PathCostFunction = Callable[[util.Vector], float]


def standard_pathcost(path: List[util.Move], start: StateType, walls: array.Array,
                      cost_fn: PathCostFunction = lambda x: 1
                      ) -> float:
    """
    A helper function that calculates the cost of a list of moves,
    with the possibility to give a cost function that defines
    the cost of each move.
    """
    vector = start
    cost = 0
    for direction in path:
        vector += direction.vector
        if walls[vector]:
            return float('inf')
        cost += cost_fn(direction.vector)
    return cost


class PositionSearchRepresentation(SearchRepresentation[util.Vector]):
    """
    A search representation that has as its goal a certain position.
    Its state type is a Vector.
    """
    PositionSuccessor = Successor[util.Vector]  # the successor type is based on the state type (Vector)

    def __init__(self, gstate: gamestate.Gamestate,
                 goal: util.Vector = util.Vector(1, 1),
                 cost_fn: PathCostFunction = lambda x: 1) -> None:
        super().__init__(gstate)
        self.start_state = gstate.pacman
        self.goal = goal
        self.cost_fn = cost_fn
        self.walls = gstate.walls

    @property
    def start(self) -> util.Vector:
        """
        The initial state of the representation,
        from which searching begins.
        """
        return self.start_state

    def is_goal(self, state: util.Vector) -> bool:
        """
        Whether the given state is a goal state in this representations.
        The first line should be `super().is_goal(pacpos)`,
        where `pacpos` is the position of pacman in the given state,
        in order for SearchAgents's cell values to function.
        """
        super().is_goal(state)
        return state == self.goal

    def successors(self, state) -> List[PositionSuccessor]:
        """
        Get all successor states of the given state in this representation.
        """
        successors = []
        for move in util.Move.no_stop:
            new_vector = state + move.vector
            if not self.walls[new_vector]:
                cost = self.cost_fn(new_vector)
                successor = (new_vector, [move], cost)
                successors.append(successor)
        return successors

    def pathcost(self, path: List[util.Move]) -> float:
        """
        Get the path cost of the given list of moves (executed from the start state).
        """
        return standard_pathcost(path, self.start, self.walls, self.cost_fn)


# the search state type for the AllDotSearchRepresentation.
# this state type consists of a tuple of two values:
# a vector indicating the position of Pacman,
# and a list of Vectors indicating the positions of dots in the maze.
AllDotSearchState = NamedTuple('AllDotSearchState', [('vector', util.Vector), ('dots', FrozenSet[util.Vector])])


class AllDotSearchRepresentation(SearchRepresentation[AllDotSearchState]):
    """
    This representation defines a search space where the goal is to find all dots in the maze.
    """
    AllDotSuccessor = Successor[AllDotSearchState]  # the successor type is based on the state type

    def __init__(self, gstate: gamestate.Gamestate) -> None:
        super().__init__(gstate)
        self.start_state = AllDotSearchState(gstate.pacman, frozenset(gstate.dots.list()))
        self.walls = gstate.walls

    @property
    def start(self) -> AllDotSearchState:
        """
        The initial state of the representation,
        from which searching begins.
        """
        return self.start_state

    def is_goal(self, state: AllDotSearchState) -> bool:
        """
        Whether the given state is a goal state in this representations.
        The first line should be `super().is_goal(pacpos)`,
        where `pacpos` is the position of pacman in the given state,
        in order for SearchAgents's cell values to function.
        """
        super().is_goal(state.vector)
        return not state.dots

    def successors(self, state: AllDotSearchState) -> List[AllDotSuccessor]:
        """
        Get all successor states of the given state in this representation.
        """
        successors = []
        for move in util.Move.no_stop:
            new_vector = state.vector + move.vector
            if not self.walls[new_vector]:
                new_dots = state.dots - {new_vector}
                successor = (AllDotSearchState(new_vector, new_dots), [move], 1)
                successors.append(successor)
        return successors

    def pathcost(self, path: List[util.Move]) -> float:
        """
        Get the path cost of the given list of moves (executed from the start state).
        """
        return standard_pathcost(path, self.start_state.vector, self.walls)


"""
Search methods
"""

# A search method is a function (callable) which takes a search representation
# and returns a list of moves that solves the representation (goes from start to goal)
SearchMethod = Callable[[SearchRepresentation[Any]], List[util.Move]]


# noinspection PyUnusedLocal
def cheating(representation: SearchRepresentation[Any]) -> List[util.Move]:
    """
    The cheating search method uses a predefined set of moves
    to solve a layout (only some layouts are defined).
    """
    # get layout name from command line arguments
    if '-l' in sys.argv:
        layout = sys.argv[sys.argv.index('-l') + 1]
    elif '--layout' in sys.argv:
        layout = sys.argv[sys.argv.index('--layout') + 1]
    else:
        layout = 'mediumClassic'

    # define abbreviations for moves
    moves = {'u': util.Move.up,
             'r': util.Move.right,
             'd': util.Move.down,
             'l': util.Move.left}

    # define cheats for layouts
    cheats = {'tinyMaze': 'ddldlldl'}

    if layout not in cheats:
        raise NotImplementedError('cheat moves have not been defined for this layout')

    return [moves[move] for move in cheats[layout]]


"""
Search heuristic
"""

# a search heuristic is a function (callable) that takes two arguments:
# a search state and a search representation. it returns a number
# representing an approximation (lower bound) of the cost from the given state
# to the goal of the given representation
# not all heuristics are generic: some are only useful for certain representations
SearchHeuristic = Callable[[StateType, SearchRepresentation[StateType]], float]


# noinspection PyUnusedLocal
def null(vector: util.Vector, representation: SearchRepresentation[Any]) -> int:
    """
    The null heuristic is a trivial lower bound. It is a useless but valid heuristic.
    """
    return 0


def manhattan(vector: util.Vector, representation: PositionSearchRepresentation) -> int:
    """
    The manhattan heuristic uses the Manhattan distance to the goal to determine its value.
    """
    return util.manhattan(vector, representation.goal)


def euclidean(vector: util.Vector, representation: PositionSearchRepresentation) -> float:
    """
    The euclidean heuristic uses the Euclidean distance to the goal to determine its value.
    """
    return util.euclidean(vector, representation.goal)
