"""
This file describes the Pacman game state model and game logic
"""

from typing import List

from . import array, layouts, util


class Gamestate:
    PACMAN_ID = 0  # the index of the pacman agent

    SCARED_TIME = 40  # amount of moves that ghosts are scared when Pacman eats a pellet

    SCORE_GET_DOT = 10
    SCORE_GET_ALL_DOTS = 500
    SCORE_GET_PELLET = 5
    SCORE_GET_GHOST = 200
    SCORE_TICK_PENALTY = -1  # penalty applied for each turn of the game
    SCORE_DIE_PENALTY = -500

    # After 100 ticks, die.
    MAX_TICKS = 100  # maximum amount of turns before Pacman dies automatically

    def __init__(self, arr: array.Array, agents: List[util.Vector] = None) -> None:
        """
        :param arr: the initial layout
        :param agents: the initial locations of all agents. Pacman is agent 0
        """
        self._statics = arr.copy()
        # agents contains the current locations of all agents
        if agents:
            self.agents = agents.copy()
        else:
            self.agents = arr.list(layouts.LayoutObject.pacman) + arr.list(layouts.LayoutObject.ghost)
        for x, y in self.active_agents:  # clear floor beneath agents
            self._statics[x, y] = layouts.LayoutObject.empty
        self.starts = self.agents.copy()  # remember start locations
        self.facings = [util.Move.stop] * len(self.agents)  # the way that each agent is facing
        self._timers = [0] * len(self.agents)  # all agents' scared timers (Pacman's is not used)
        self.score = 0  # current score
        self._tick = 0  # current turn

    @property
    def pacman(self) -> util.Vector:
        """
        Pacman's current location
        """
        return self.agents[self.PACMAN_ID]

    @property
    def ghosts(self) -> List[util.Vector]:
        """
        Current locations of all ghosts
        """
        return self.agents[self.PACMAN_ID + 1:]

    @property
    def timers(self) -> List[int]:
        """
        Current scared timers of all ghosts
        """
        return self._timers[1:]

    @property
    def active_agents(self) -> List[util.Vector]:
        """
        Locations of agents that are currently alive
        """
        return [agent for agent in self.agents if agent]

    @property
    def walls(self) -> array.IndicatorArray:
        """
        Array indicating layout of walls
        """
        return self._statics.indicate(layouts.LayoutObject.wall)

    @property
    def dots(self) -> array.IndicatorArray:
        """
        Array indicating layout of dots
        """
        return self._statics.indicate(layouts.LayoutObject.dot)

    @property
    def pellets(self) -> array.IndicatorArray:
        """
        Array indicating layout of pellets
        """
        return self._statics.indicate(layouts.LayoutObject.pellet)

    @property
    def shape(self) -> util.Vector:
        """
        Tuple indicating the shape of the layout
        """
        return self._statics.shape

    @property
    def copy(self):
        """
        Create an independent copy of the gamestate
        """
        copy = Gamestate(array.Array([]))
        copy._statics = self._statics.copy()
        copy.agents = self.agents.copy()
        copy.starts = self.starts.copy()
        copy.facings = self.facings.copy()
        copy._timers = self._timers.copy()
        copy.score = self.score
        copy._tick = self._tick
        return copy

    def apply_move(self, agent_id: int, move: util.Move):
        """
        Logic for applying an agent's move to the gamestate. Gamestate is modified in-place.
        :param agent_id: the ID of the agent
        :param move: the agent's move
        :return:
        """
        if not self.agents[agent_id]:  # agent is dead
            return

        if not move:  # agent made no move or was not allowed to move (current move executing)
            move = util.Move.stop

        self.facings[agent_id] = move  # update agent's facing

        vector = self.agents[agent_id]  # get agent's current location
        new_vector = vector + move.vector  # calculate new location
        self.agents[agent_id] = new_vector  # set new location

        if self._timers[agent_id]:  # if agent is currently scared, reduce their timer
            self._timers[agent_id] -= 1

        if agent_id == self.PACMAN_ID:  # if agent is Pacman, apply turn penalty
            self.score += self.SCORE_TICK_PENALTY

        if self.walls[new_vector]:  # if agent moves into a wall, end the game
            if agent_id == self.PACMAN_ID:
                self.score += self.SCORE_DIE_PENALTY
            raise RuntimeError(f'agent {agent_id} walked into a wall at {new_vector}')

        if agent_id == self.PACMAN_ID:

            if new_vector in self.ghosts:  # if Pacman runs into a ghost, resolve the encounter
                ghost_id = self.ghosts.index(new_vector) + 1
                self._resolve_encounter(ghost_id)

            if self.dots[new_vector]:  # if Pacman runs into a dot, eat it and reward score
                self._statics[new_vector] = layouts.LayoutObject.empty
                self.score += self.SCORE_GET_DOT
                if not self.dots.list():
                    self.score += self.SCORE_GET_ALL_DOTS

            if self.pellets[new_vector]:  # if Pacman runs into a pellet, eat it, reward score, and set timers
                self._statics[new_vector] = layouts.LayoutObject.empty
                self.score += self.SCORE_GET_PELLET
                self._timers[1:] = [self.SCARED_TIME] * len(self._timers[1:])

        else:

            if new_vector == self.pacman:  # if a ghost runs into Pacman, resolve the encounter
                self._resolve_encounter(agent_id)

    def _resolve_encounter(self, ghost_id: int):
        """
        Resolve an encounter between Pacman and a ghost
        :param ghost_id:
        """
        if self._timers[ghost_id]:  # pacman kills the ghost
            self.kill(ghost_id)
            self.score += self.SCORE_GET_GHOST
        else:  # the ghost kills pacman
            self.kill(self.PACMAN_ID)
            self.score += self.SCORE_DIE_PENALTY

    def can_move(self, agent_id: int):
        """
        Check whether a certain agent is allowed to move.
        To be allowed to move, an agent needs to be alive and if it is scared,
        the current turn number must be even. This makes scared ghosts move
        twice as slowly as regular agents.
        """
        return self.agents[agent_id] and (not self._timers[agent_id] or self._tick % 2 == 0) and not self.gameover

    def legal_moves_vector(self, vector: util.Vector):
        """
        Get all moves that are possible from a particular location (taking walls into consideration).
        """
        moves = set()
        for move in util.Move:
            new_vector = vector + move.vector
            if not self.walls[new_vector]:
                moves.add(move)
        return moves

    def legal_moves_id(self, agent_id: int):
        """
        Get all moves from a particular agent's current location (taking walls into consideration).
        """
        return self.legal_moves_vector(self.agents[agent_id])

    @property
    def win(self) -> bool:
        """
        Whether Pacman has won the game. This is the case when all dots have been eaten.
        """
        return not self.loss and not self.dots.list()

    @property
    def loss(self) -> bool:
        """
        Whether Pacman has lost the game. This is the case when Pacman is dead.
        """
        return not self.pacman

    @property
    def gameover(self) -> bool:
        """
        Whether the game is over. This is the case when Pacman has won or lost the game.
        """
        return self.win or self.loss

    def tick(self):
        """
        Increase the game's turn number.
        """
        self._tick += 1

        if self._tick == self.MAX_TICKS:
            self.destroy(self.PACMAN_ID)
            print(f'WARNING: max number of ticks reached ({self.MAX_TICKS}) pacman was destroyed')

    def kill(self, agent_id: int):
        """
        Kill a certain agent. In the case of ghosts, this resets them to their starting location.
        """
        if agent_id == self.PACMAN_ID:
            self.agents[agent_id] = None
        else:
            self.agents[agent_id] = self.starts[agent_id]
            self._timers[agent_id] = 0

    def destroy(self, agent_id: int):
        """
        Destroy a certain agent. Contrary to `kill`, ghosts do not reset with `destroy`.
        """
        self.agents[agent_id] = None
        if agent_id == 0:  # Pacman forcefully destroyed as penalty (max ticks / timeout); subtract score
            self.score += self.SCORE_DIE_PENALTY

    def successor(self, agent_id: int, move: util.Move):
        """
        Get a new gamestate based on this one, where the given agent has executed the given move.
        """
        successor = self.copy
        successor.apply_move(agent_id, move)
        return successor

    def successors(self, agent_id: int):
        """
        Get all possible gamestates following this one, in which the given agent had executed a single move.
        """
        return [self.successor(agent_id, move) for move in self.legal_moves_vector(self.agents[agent_id])]

    def __repr__(self):
        """
        Official string representation.
        """
        data = str({'agents': self.agents,
                    'facings': self.facings,
                    'timers': self.timers,
                    'dots': self.dots.list(),
                    'pellets': self.pellets.list(),
                    'score': self.score,
                    'tick': self._tick})
        return f'Gamestate({data})'

    def __str__(self):
        """
        Informal string representation.
        """
        layout = self._statics.copy()
        if self.pacman:
            layout[self.pacman] = layouts.LayoutObject.pacman
        for ghost, timer in zip(self.ghosts, self.timers):
            if ghost:
                if timer:
                    layout[ghost] = layouts.LayoutObject.ghost_scared
                else:
                    layout[ghost] = layouts.LayoutObject.ghost
        return str(layout.transpose.mirror_hor) + f'\nScore: {self.score}'
