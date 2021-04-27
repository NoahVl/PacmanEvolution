# Noah van der Vleuten (s1018323)
# Jozef Coldenhoff (s1017656)

import queue
from pacman import agents, gamestate, search, util

import ass2


class CornersSearchRepresentation(search.SearchRepresentation):
    def __init__(self, gstate):
        super().__init__(gstate)
        self.walls = gstate.walls
        self.start_position = gstate.pacman
        left, bottom = 1, 1
        right, top = gstate.shape - 2 * util.Vector.unit
        self.corners = frozenset([util.Vector(left, bottom),
                                  util.Vector(left, top),
                                  util.Vector(right, bottom),
                                  util.Vector(right, top)])

    @property
    def start(self):
        return self.start_position, (False, False, False, False)

    def is_goal(self, state):
        position, corners_tuple = state
        super().is_goal(position)
        corners_bool_list = list(corners_tuple)

        for boolean in corners_bool_list:
            if not boolean:
                return False

        return True

    def successors(self, state):
        position, corners_tuple = state
        successors = []

        for move in util.Move.no_stop:
            new_vector = position + move.vector

            if not self.walls[new_vector]:

                corners_bool_list = list(corners_tuple)

                corners_list = list(self.corners)

                if new_vector in corners_list:
                    index_position = corners_list.index(new_vector)
                    if new_vector in self.corners:
                        corners_bool_list[index_position] = True

                successor = ((new_vector, tuple(corners_bool_list)), [move], 1)
                successors.append(successor)

        return successors

    def pathcost(self, path):
        return search.standard_pathcost(path, self.start_position, self.walls)


def corners_heuristic(state, representation):
    """
    Calculates the Manhattan distance to the closest unvisited corner,
    plus the Manhattan distance to the other unvisited corners.

    This heuristic is admissible because the cost of the manhattan distance of these corners relative to each other is
    never greater than the actual path cost of getting there.

    :param state: this is the state of the game containing the position and visited corners of Pacman.
    :param representation: (search.PositionSearchRepresentation) the search representation being passed in.
    :returns: (number) the numerical result of the heuristic.
    """

    # List of corner coordinates.
    corners = list(representation.corners)
    position, corners_visited = state

    result = 0
    future_corners_visited = list(corners_visited)
    future_position = position

    for i in range(len(corners)):

        distance_to_corners = [0, 0, 0, 0]

        for num_corner, corner in enumerate(future_corners_visited):
            distance_to_corners[num_corner] = util.manhattan(future_position, corners[num_corner])

        num_closest = 0

        for num_corner, distance_corner in enumerate(distance_to_corners):

            if future_corners_visited[num_closest]:
                num_closest = num_corner
            if not future_corners_visited[num_corner] and distance_corner < distance_to_corners[num_closest]:
                num_closest = num_corner

        if not future_corners_visited[num_closest]:
            result += distance_to_corners[num_closest]
            future_position = corners[num_closest]
            future_corners_visited[num_closest] = True
        else:
            break

    return result


def dots_heuristic(state, representation):
    """
    Calculates the Manhattan distance from this state to all the pellets from this state,
    then sorts them from high to low to find the 3 pellets that are furthest away.
    We add the manhattan distance of the third furthest away pellet plus the distance of the 3rd to the 2nd plus the
    distance from the 2nd to the furthest away pellet to the heuristic.

    This heuristic is always admissible because the manhattan distance to all these points will never overestimate the
    actual cost of going there.

    :param state: this is the state of the game containing the position and visited corners of Pacman.
    :param representation: (search.PositionSearchRepresentation) the search representation being passed in.
    :returns: (number) the numerical result of the heuristic.
    """
    position = state[0]

    distance_list = [(util.manhattan(position, x), x) for x in state.dots]
    heuristic = 0
    distance_list.sort(reverse=True)
    if len(distance_list) > 2:
        heuristic += distance_list[2][0]
        heuristic += util.manhattan(distance_list[2][1], distance_list[1][1])
        heuristic += util.manhattan(distance_list[1][1], distance_list[0][1])
    return heuristic


class ClosestDotSearchAgent(agents.SearchAgent):
    def prepare(self, gstate):
        self.actions = []
        pacman = gstate.pacman
        while gstate.dots:
            next_segment = self.path_to_closest_dot(gstate)
            self.actions += next_segment
            for move in next_segment:
                if move not in gstate.legal_moves_vector(gstate.agents[self.id]):
                    raise Exception('path_to_closest_dot returned an illegal move: {}, {}'.format(move, gstate))
                gstate.apply_move(self.id, move)

        print(f'[ClosestDotSearchAgent] path found with length {len(self.actions)}'
              f' and pathcost {search.standard_pathcost(self.actions, pacman, gstate.walls)}')

    @staticmethod
    def path_to_closest_dot(gstate):
       return ass2.breadthfirst(AnyDotSearchRepresentation(gstate))


class AnyDotSearchRepresentation(search.PositionSearchRepresentation):
    def __init__(self, gstate):
        super().__init__(gstate)
        self.dots = gstate.dots

    def is_goal(self, state):
        return self.dots[state] is True

class ApproximateSearchAgent(agents.SearchAgent):
    def prepare(self, gstate):
        pass

    def move(self, gstate):
        if self.actions:
            return self.actions.pop(0)
        else:
            self.actions = approx_search(search.AllDotSearchRepresentation(gstate))
            return self.actions.pop(0)


def approx_search(representation: search.PositionSearchRepresentation) -> list:
    """
    Search function that finds the closest node and returns the list of moves to that node,
    also makes sure that Pacman finished the right part of the maze before beginning to work on the left part.
    """
    frontier = queue.PriorityQueue()
    frontier.put((0, (representation.start, [], 0)))
    dots = list(representation.start[1])

    # Finds all the nodes that are to the right of the middle.
    right_dots = [x for x in dots if x[0] < representation.walls.shape[0] / 2]

    # Finds all the nodes that are to the left of the middle.
    left_dots = [x for x in dots if x[0] > representation.walls.shape[0] / 2]

    explored = set()

    while not frontier.empty():
        _, successor = frontier.get()
        state, path, cost = successor

        if state in explored:
            continue
        explored.add(state)

        # Returns if a path to the closest node in the right part of the map is found.
        if state[0] in left_dots and not right_dots:
            return path

        # Returns if a path to the closest node in the left part of the map is found.
        elif state[0] in right_dots:
            return path

        for successorState, actions, actionCost in representation.successors(state):
            if successorState not in explored:
                new_cost = cost + actionCost + right_heuristic(successorState, dots)
                frontier.put((new_cost, (successorState, path + actions, cost + actionCost)))

    return None


def right_heuristic(state, dots):
    """
    Heuristic that weights the path by taking the node that is furthest right from Pacman.
    """
    heuristic = 0

    # Finds all the dots that are to the right of Pacman.
    right_dots = [x for x in dots if x[0]< state[0][0]]

    # Sorts the list by comparing the x coordinates.
    right_dots.sort(key= lambda x: x[0])

    # Returns the distance to the most right node.
    if right_dots:
        heuristic = util.manhattan(right_dots[0], state[0])
    return heuristic
