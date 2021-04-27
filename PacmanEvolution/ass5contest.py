"""
Modified contest agent to execute NEAT's neural net by loading a genome and config in the python-neat neural net.
"""

import exceptions
import numbers
import random
from pacman import agents, gamestate, util, distancer
import collections


import neat


class ContestAgent(agents.PacmanAgent):

    def prepare(self, gstate, genome, config):
        """
        Use this method for initializing tour ContestAgent.
        The provided stump only calls the prepare of the mother class.
        You might want to add other things, for instance
        calling the precompute_distances() method of the Distancer class
        """
        super().prepare(gstate)

        # precompute distances:
        self.distances = collections.defaultdict(lambda: float('inf'))
        self.distances = distancer.Distancer(gstate)
        self.distances.precompute_distances()

        # initialize network
        self.net = neat.nn.recurrent.RecurrentNetwork.create(genome, config)

    def move(self, gstate: gamestate.Gamestate) -> util.Move:
        """
        This method gets called every turn, asking the agent
        what move they want to make based on the current gamestate.
        """

        # Get distance to closest dot.
        closest_dot = [[(self.distances.get_distance(gstate.pacman, dot_pos), dot_pos)] for dot_pos in gstate.dots.list()]
        closest_dot = min(closest_dot)

        closest_dot_x, closest_dot_y = closest_dot[0][1] - gstate.pacman
        # closest_dot_dist = closest_dot[0][0]

        closest_ghost_x = 0
        closest_ghost_y = 0
        closest_ghost_dist = -1

        if gstate.ghosts:
            # Get distance to closest ghost.
            closest_ghost = [[(self.distances.get_distance(gstate.pacman, ghost_pos), ghost_pos)] for ghost_pos in gstate.ghosts]
            closest_ghost = min(closest_ghost)

            closest_ghost_x, closest_ghost_y = closest_ghost[0][1] - gstate.pacman
            closest_ghost_dist = closest_ghost[0][0]

        moves = []

        if util.Move.up in gstate.legal_moves_id(0):
            moves.append(1)
        else:
            moves.append(0)

        if util.Move.down in gstate.legal_moves_id(0):
            moves.append(1)
        else:
            moves.append(0)

        if util.Move.right in gstate.legal_moves_id(0):
            moves.append(1)
        else:
            moves.append(0)

        if util.Move.left in gstate.legal_moves_id(0):
            moves.append(1)
        else:
            moves.append(0)

        # Give the neural net input.
        network_input = (moves[0], moves[1], moves[2], moves[3],
                         closest_ghost_x, closest_ghost_y, closest_ghost_dist,
                         closest_dot_x, closest_dot_y)

        # Get network output
        network_output = self.net.activate(network_input)

        best_index = 0
        best_score = 0

        for index, score in enumerate(network_output):
            if score > best_score:
                best_index = index
                best_score = score

        # Check what move we have to return based on which output is highest:
        # 0: UP
        # 1: DOWN
        # 2: RIGHT
        # 3: LEFT
        best_move = util.Move.by_index(best_index)

        # Check if the "best" move is not to go in the wall.
        # We should punish the agent immediately but it can't see the walls yet.
        legal_moves = gstate.legal_moves_id(0)

        if best_move not in legal_moves:
            return util.Move.stop

        return best_move


    def evaluate(self, gstate: gamestate.Gamestate, move: util.Move):
        """
        Not needed for this implementation I think because the network does the evaluation itself
        """
        successor = gstate.successor(self.id, move)
        return successor.score
