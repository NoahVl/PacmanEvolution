"""
This file describes the agents that are available in the Pacman game.
"""

import abc
import numbers
import random
from typing import Any, Callable, List, Type, Union

from . import array, displays, gamestate, search, tech_util, util


class Agent(metaclass=abc.ABCMeta):
    """
    An agent is an active participant in the Pacman game.
    Pacman himself and the ghosts are agents.
    """

    def __init__(self, agent_id):
        self.id = agent_id

    def prepare(self, gstate: gamestate.Gamestate) -> None:
        """
        Called before the start of a game, this method
        allows the agent to make any necessary preparations
        based on the initial gamestate.
        """
        pass

    @abc.abstractmethod
    def move(self, gstate: gamestate.Gamestate) -> util.Move:
        """
        This method gets called every turn, asking the agent
        what move they want to make based on the current gamestate.
        """
        pass


class PacmanAgent(Agent, abc.ABC):
    """
    A subclass of Agent, this class describes the Pacman agent specifically.
    """

    def __init__(self):
        super().__init__(0)
        self._cell_values = None

    @property
    def cell_values(self) -> array.Array[Union[numbers.Number, None]]:
        """
        A Pacman agent can determine an arbitrary numerical value for
        each cell of the game grid. These values are used at the start
        of the game (after preparation) to be drawn onto the game
        graphics. This is mostly used by the SearchAgent to visualise
        the node expansion order.
        """
        return self._cell_values

    def prepare(self, gstate: gamestate.Gamestate):
        """
        Called before the start of a game, this method
        allows the agent to make any necessary preparations
        based on the initial gamestate.
        """
        self._cell_values = array.Array([[None] * gstate.shape.y for _ in range(gstate.shape.x)])

    @abc.abstractmethod
    def move(self, gstate: gamestate.Gamestate) -> util.Move:
        """
        This method gets called every turn, asking the agent
        what move they want to make based on the current gamestate.
        """
        pass


class KeyboardAgent(PacmanAgent):
    """
    This agent is controllable by keyboard input.
    """

    def __init__(self, display: displays.Display):
        super().__init__()
        self.display = display

    def move(self, gstate: gamestate.Gamestate) -> util.Move:
        """
        This method gets called every turn, asking the agent
        what move they want to make based on the current gamestate.
        """
        sym = self.display.get_keypress()
        if sym is not None:
            moves = {'Up': util.Move.up,
                     'Down': util.Move.down,
                     'Right': util.Move.right,
                     'Left': util.Move.left}
            if sym in moves:
                move = moves[sym]
                if move in gstate.legal_moves_vector(gstate.agents[self.id]):
                    return move
        return util.Move.stop


class GoLeftAgent(PacmanAgent):
    """
    This agent always goes left, if this is a valid move (not a wall)..
    """

    def move(self, gstate: gamestate.Gamestate) -> util.Move:
        """
        This method gets called every turn, asking the agent
        what move they want to make based on the current gamestate.
        """
        vector = gstate.agents[self.id]
        if util.Move.left in gstate.legal_moves_vector(vector):
            return util.Move.left
        else:
            return util.Move.stop


class GoRightAgent(PacmanAgent):
    """
    This agent always goes right, if this is a valid move (not a wall)..
    """

    def move(self, gstate: gamestate.Gamestate) -> util.Move:
        """
        This method gets called every turn, asking the agent
        what move they want to make based on the current gamestate.
        """
        vector = gstate.agents[self.id]
        if util.Move.right in gstate.legal_moves_vector(vector):
            return util.Move.right
        else:
            return util.Move.stop


"""
Search agents
"""


class SearchAgent(PacmanAgent):
    """
    This agent relies on search to find a path to its goal.
    In order to execute a search, the agent needs at least two things.
    First, it needs a Search Representation. This is an object
    that tell the agent what the search space looks like (see search.py).
    Second, it needs a Search Method. This is a function that performs
    the actual search, based on the Search Representation (see search.py).
    If so, the agent also needs to receive this.
    """

    def __init__(self, representation_type: Type[search.SearchRepresentation[Any]], method: search.SearchMethod):
        super().__init__()
        self.representation_type = representation_type
        self.method = method
        self.actions = None

    def prepare(self, gstate: gamestate.Gamestate) -> None:
        """
        Called before the start of a game, this method
        allows the agent to make any necessary preparations
        based on the initial gamestate.
        """
        super().prepare(gstate)
        print(f'[SearchAgent] using method {self.method.__name__}')
        print(f'[SearchAgent] using representation {self.representation_type.__name__}')

        # here, the SearchAgent does all the work
        # of running the Search Method and getting
        # the list of actions that it will execute
        representation = self.representation_type(gstate)
        self.actions = self.run_search(representation)
        self._cell_values = representation.expansion_order

        if self.actions is not None:
            print(f'[SearchAgent] path found with length {len(self.actions)}'
                  f' and pathcost {representation.pathcost(self.actions)}')
            print(f'[SearchAgent] search nodes expanded: {representation.expansion_count}')
        else:
            print('Warning! None returned, search failed!')

    def move(self, gstate: gamestate.Gamestate) -> util.Move:
        """
        This method gets called every turn, asking the agent
        what move they want to make based on the current gamestate.
        """
        # the SearchAgent uses the list of actions that
        # it calculated in `prepare` to give each move in order
        if self.actions:
            return self.actions.pop(0)
        else:
            return util.Move.stop

    def run_search(self, representation: search.SearchRepresentation) -> List[util.Move]:
        """
        The SearchAgent runs the actual Method,
        giving it the Representation and possibly Heuristic.
        Some Representations will give multidimensional
        lists of Moves (lists of lists), so we need to
        flatten the result to a simple list.
        """
        return tech_util.flatten_2d(self.method(representation))


class StayLeftSearchAgent(SearchAgent):
    """
    This SearchAgent prefers to stay left,
    and achieves this through an appropriate SearchRepresentation.
    """

    def prepare(self, gstate: gamestate.Gamestate) -> None:
        """
        Called before the start of a game, this method
        allows the agent to make any necessary preparations
        based on the initial gamestate.
        """

        def cost_fn(pos: util.Vector):
            return 2 ** pos.x
        self.representation_type = lambda gstate: search.PositionSearchRepresentation(gstate, cost_fn=cost_fn)
        super().prepare(gstate)


class StayRightSearchAgent(SearchAgent):
    """
    This SearchAgent prefers to stay right,
    and achieves this through an appropriate SearchRepresentation.
    """

    def prepare(self, gstate: gamestate.Gamestate) -> None:
        """
        Called before the start of a game, this method
        allows the agent to make any necessary preparations
        based on the initial gamestate.
        """
        def cost_fn(pos: util.Vector):
            return 0.5 ** pos.x
        self.representation_type = lambda gstate: search.PositionSearchRepresentation(gstate, cost_fn=cost_fn)
        super().prepare(gstate)


"""
Reflex agents
"""


class ReflexAgent(PacmanAgent, abc.ABC):
    """
    This agent bases its action on reflexes.
    Each turn, it evaluates which single move results in the best
    next gamestate. It then executes that move.
    """

    def move(self, gstate: gamestate.Gamestate) -> util.Move:
        """
        This method gets called every turn, asking the agent
        what move they want to make based on the current gamestate.
        """
        moves = gstate.legal_moves_vector(gstate.agents[self.id])
        scores = {move: self.evaluate(gstate.copy, move) for move in moves}
        max_score = max(scores.values())
        max_moves = [move for move in moves if scores[move] == max_score]
        return random.choice(max_moves)

    @abc.abstractmethod
    def evaluate(self, gstate: gamestate.Gamestate, move: util.Move) -> numbers.Number:
        """
        This method is used by the reflex agent to determine
        the value of a given move if it would be used in a given gamestate.
        """
        pass


class ScoreReflexAgent(ReflexAgent):
    """
    This reflex agent evaluates a gamestate
    based solely on Pacman's score in that gamestate.
    """

    def evaluate(self, gstate: gamestate.Gamestate, move: util.Move) -> numbers.Number:
        """
        This method is used by the reflex agent to determine
        the value of a given move if it would be used in a given gamestate.
        """
        successor = gstate.successor(self.id, move)
        return successor.score


"""
Adversarial agents
"""

# a gamestate evaluation function takes a gamestate
# and returns some number representing how good it is
GamestateEvaluationFunction = Callable[[gamestate.Gamestate], numbers.Number]


def score_evaluate(gstate: gamestate.Gamestate) -> int:
    """
    This gamestate evaluation function simply returns the score of the gamestate
    """
    return gstate.score


class AdversarialAgent(PacmanAgent, abc.ABC):
    """
    An adversarial agent uses some sort of prediction
    of the enemy's choices in order to determine what
    is the best choice for Pacman. It only predicts choices
    up to a certain depth, and it uses an evaluation function
    to determine how good any given gamestate is for Pacman.
    """

    def __init__(self, depth: int, evaluate: GamestateEvaluationFunction):
        super().__init__()
        self.depth = depth
        self.evaluate = evaluate

    @abc.abstractmethod
    def move(self, gstate: gamestate.Gamestate):
        """
        This method gets called every turn, asking the agent
        what move they want to make based on the current gamestate.
        """
        pass


"""
Ghost agents
"""


class GhostAgent(Agent, abc.ABC):
    """
    These agents are meant to control the ghosts in the Pacman world.
    """

    def move(self, gstate: gamestate.Gamestate) -> util.Move:
        """
        This method gets called every turn, asking the agent
        what move they want to make based on the current gamestate.
        """
        options, weights = self.distribution(gstate)
        if not options:
            return util.Move.stop
        return random.choices(options, weights).pop()

    @abc.abstractmethod
    def distribution(self, gstate: gamestate.Gamestate) -> util.Distribution:
        """
        Based on the given gamestate, this method returns a Distribution
        over moves that the agent might make, with the value of each move
        representing the probability that the agent should make that move.
        """
        pass

    def valid_moves(self, gstate: gamestate.Gamestate):
        """
        This method returns the valid moves for a ghost agent.
        A ghost cannot move backwards in a corridor, except when
        that is the only move to make (a dead end).
        """
        vector = gstate.agents[self.id]
        facing = gstate.facings[self.id]
        legal_moves = set(gstate.legal_moves_vector(vector)) - {util.Move.stop}
        if len(legal_moves) == 1:
            return legal_moves
        else:
            return set(legal_moves) - {facing.opposite}


class RandomGhostAgent(GhostAgent):
    """
    A random ghost agent uses a uniform distribution over all
    possible moves, effectively making their next move random.
    """

    def distribution(self, gstate: gamestate.Gamestate) -> util.Distribution:
        """
        Based on the given gamestate, this method returns a Distribution
        over moves that the agent might make, with the value of each move
        representing the probability that the agent should make that move.
        """
        options = self.valid_moves(gstate)
        return list(options), [1] * len(options)

class ChasingGhostAgent(GhostAgent):
    """
    A semi-random ghost that chases Pacman when not scared,
    and runs away from Pacman when scared, but with fixed probability
    does a random move instead.
    """
    random_probability = 0.2

    def distribution(self, gstate: gamestate.Gamestate) -> util.Distribution:
        player_position = gstate.pacman
        ghost_position = gstate.agents[self.id]
        is_scared = gstate.timers[self.id - 1]

        # Divide random_probability among all moves
        moves = self.valid_moves(gstate)
        distr = dict((move, self.random_probability / len(moves)) for move in moves)

        # Divide 1-random_probability over all best moves (towards or away from player depending on scared timer)
        player_distances = [util.manhattan(player_position, ghost_position + move.vector) for move in moves]
        if is_scared:
            best_dist = max(player_distances)
        else:
            best_dist = min(player_distances)
        best_actions = [move for move, dist in zip(moves, player_distances) if dist == best_dist]

        for move, dist in zip(moves, player_distances):
            if move in best_actions:
                distr[move] += (1 - self.random_probability) / len(best_actions)

        return list(distr.keys()), list(distr.values())


class TrackGhostAgent(GhostAgent):
    """
    A ghost that just follows a track determined at the level start.
    """
    track_length = 10  # indication, not a guarantee

    def prepare(self, gstate: gamestate.Gamestate):
        self.track_moves, self.track_positions = self.generate_random_track(gstate, self.track_length)
        self.track_index = 0
        self.track_error = False

    def distribution(self, gstate: gamestate.Gamestate) -> util.Distribution:
        track_move = self.track_moves[self.track_index]
        move = track_move
        moves = self.valid_moves(gstate)

        if move in moves and not self.track_error:  # check track validity
            self.track_index = (self.track_index + 1) % len(self.track_positions)
        else:
            # Cannot continue on track; try to get back, otherwise wander randomly
            position = gstate.agents[self.id]
            back_on_track_moves = [move for move in moves if position + move.vector in self.track_positions and move
                                   != self.track_moves[self.track_positions.index(position + move.vector)].opposite]

            if len(back_on_track_moves) > 0:
                move = random.choice(back_on_track_moves)
                self.track_error = False
                self.track_index = self.track_positions.index(position + move.vector)
            else:
                move = random.choice(list(moves))
                self.track_error = True

        return [move], [1]

    def generate_random_track(self, gstate: gamestate.Gamestate, length: int):
        # Algorithm from original Berkeley course
        track_moves = []
        track_positions = []
        start_position = gstate.agents[self.id]

        position = start_position
        last_move = util.Move.stop
        while position != start_position or len(track_positions) == 0:
            moves = gstate.legal_moves_vector(position) - {util.Move.stop}
            index = len(track_positions)
            if len(moves) > 1:  # prevent turning back
                moves = moves - {last_move.opposite}
            if len(moves) > 1 and index < 2*self.track_length:
                new_moves = [move for move in moves if position + move.vector not in track_positions]
                if len(new_moves) > 0:  # avoid returning to a previous point on our track unless we need to return
                    moves = new_moves
            if len(moves) > 1 and self.track_length/2 < index < 4*self.track_length and position == track_positions[1]:
                new_moves = [move for move in moves if position + move.vector != start_position]
                if len(new_moves) > 0:  # avoid going back to step 1 without going back to the start afterwards.
                    moves = new_moves   # this pushes for "rounder" trajectory endings, if possible

            if len(moves) > 1:  # bias away from start in first half, towards start afterwards
                dist = util.manhattan(start_position, position)
                new_dists = [util.manhattan(start_position, position + move.vector) for move in moves]
                if index < self.track_length / 2:
                    new_moves = [move for move, new_dist in zip(moves, new_dists) if new_dist >= dist]
                elif index < 4*self.track_length:
                    new_moves = [move for move, new_dist in zip(moves, new_dists) if new_dist <= dist]
                else:  # to prevent getting stuck, we start forcing it to go back asap
                    new_moves = [(move, track_positions.index(position + move.vector)) for move in moves
                                 if position + move.vector in track_positions]
                    if len(new_moves) > 0:
                        new_moves = [min(new_moves, key=lambda x: x[1])[0]]
                if len(new_moves) > 0:
                    moves = new_moves

            last_move = random.choice(list(moves))
            track_positions.append(position)
            track_moves.append(last_move)
            position = position + last_move.vector

        return track_moves, track_positions
