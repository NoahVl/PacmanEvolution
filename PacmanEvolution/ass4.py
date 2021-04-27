# Noah van der Vleuten (s1018323)
# Jozef Coldenhoff (s1017656)

import exceptions
import random

from pacman import agents, gamestate, util


class BetterReflexAgent(agents.ReflexAgent):
    def evaluate(self, gstate, move):
        # Get the next moves of Pacman.
        next_position = gstate.pacman + move.vector
        score = 0  # Initialize the score.

        # Calculate the distance to all the food.
        distance_to_dots = [util.manhattan(x, next_position) for x in gstate.dots.list()]
        distance_to_dots.sort()  # Sort the distances in ascending order.

        for ghost in gstate.ghosts:

            # Get the positions of the ghost in the future.
            individual_ghost_move = gstate.legal_moves_vector(ghost)

            # Add the ghosts to their potential future positions.
            individual_ghost_position = [ghost + x.vector for x in individual_ghost_move]

            # Check if the position is legal for Pacman.
            if next_position in individual_ghost_position:
                # If not return minus infinity, meaning Pacman will try not to do this if there are other options.
                return float('-inf')
            if gstate.dots[next_position]:
                score += float('inf')

        # Subtract the distance to the closest dot off of the score.
        score -= distance_to_dots[0]
        return score


class MinimaxAgent(agents.AdversarialAgent):
    def move(self, gstate):
        score, best_move = self.minimax(gstate, self.depth, True)
        return best_move

    def minimax(self, gstate, depth, maximizer):

        # if we are in a leaf node or the game is a loss or win we just return the evaluation of that node
        if depth is 0 or gstate.loss or gstate.win:
            return self.evaluate(gstate), util.Move.stop

        # if the current agent is a maximizer execute the following code
        if maximizer:

            # gets all legal actions of Pacman
            legal_actions = list(gstate.legal_moves_id(0))

            # makes a list of all the scores of the successors recursively
            scores = [self.minimax(gstate.successor(0, x), depth, False)[0] for x in legal_actions]

            # takes the maximum found score in the list
            best_score = max(scores)

            # takes all the indexes of the best scores and fills a list with the corresponding moves
            best_actions = [x for x in range(len(scores)) if scores[x] is best_score]

            # returns a random move of the moves with the best score and the score itself
            return best_score, legal_actions[random.choice(best_actions)]

        # if the current agent is a minimizer execute the following code
        else:

            # gets all legal actions of the ghost
            legal_actions = list(gstate.legal_moves_id(1))

            # makes a list of all the scores of the successors recursively
            scores = [self.minimax(gstate.successor(1, x), depth - 1, True)[0] for x in legal_actions]

            # takes the minimum found score in the list
            best_score = min(scores)

            # takes all the indexes of the best scores and fills a list with the corresponding moves
            best_actions = [x for x in range(len(scores)) if scores[x] is best_score]

            # returns a random move of the moves with the best score and the score itself
            return best_score, legal_actions[random.choice(best_actions)]


class AlphabetaAgent(agents.AdversarialAgent):
    def move(self, gstate):
        score, best_move = self.alpha_beta(gstate, self.depth, True, float('-inf'), float('inf'))
        return best_move

    def alpha_beta(self, gstate, depth, maximizer, alpha, beta):
        # if we are in a leaf node or the game is a loss or win we just return the evaluation of that node
        if depth is 0 or gstate.loss or gstate.win:
            return self.evaluate(gstate), util.Move.stop

        # if the current agent is a maximizer execute the following code
        if maximizer:
            # gets all legal actions of Pacman
            legal_actions = list(gstate.legal_moves_id(0))
            # initialise the best score
            best_score = float('-inf')
            # initialise the best action
            best_action = util.Move.stop
            # loop through the actions
            for move in legal_actions:
                # generates the score associated with the move recursively
                score = self.alpha_beta(gstate.successor(0, move), depth, False, alpha, beta)[0]
                # keeps track of the best score and move so far
                if score > best_score:
                    best_score = score
                    best_action = move
                # checks if alpha can be changed
                alpha = max(best_score, alpha)
                # prunes the branch if possible
                if beta <= alpha:
                    break
            return best_score, best_action

        # if the current agent is a minimizer execute the following code
        else:
            # gets all legal actions of the ghost
            legal_actions = list(gstate.legal_moves_id(1))
            # initialise the best score
            best_score = float('inf')
            # initialise the best action
            best_action = util.Move.stop
            # loop through the actions
            for move in legal_actions:
                # generates the score associated with the move recursively
                score = self.alpha_beta(gstate.successor(1, move), depth - 1, True, alpha, beta)[0]
                # keeps track of the best score and move so far
                if score < best_score:
                    best_score = score
                    best_action = move
                # checks if beta can be changed
                beta = min(best_score, beta)
                # prunes the branch if possible
                if beta <= alpha:
                    break
            return best_score, best_action


def better_evaluate(gstate):

    # If Pacman loses in this state, return -inf.
    if gstate.loss:
        return float('-inf')

    # This makes sure that Pacman doesn't win while the ghost can still be killed
    elif gstate.win and (gstate.pellets or gstate.timers[0] > 0):
        return 0

    # This makes sure that if the ghost is scared Pacman will go to the ghost and try to kill it
    elif gstate.timers[0] > 0:
        return (1 / util.euclidean(gstate.pacman, gstate.agents[1])) + gstate.score + 1 / random.randint(10, 30)

    # If there are still pellets in the game Pacman will go to the nearest one
    elif gstate.pellets and not gstate.timers[0] > 0:
        pellets = [util.euclidean(x, gstate.pacman) for x in gstate.pellets.list()]
        pellets.sort()
        return 1 / pellets[0] + gstate.score + 1 / random.randint(10, 30)

    # If Pacman used all pellets and killed the ghost as much at possible it will move to the nearest dot
    elif gstate.dots:
        dots = gstate.dots.list()
        dots.sort(key=lambda x: util.euclidean(x, gstate.pacman))
        return 1 / util.euclidean(gstate.pacman, dots[0]) + gstate.score + 1 / random.randint(10, 30)

    # PS we add some noise to all the evaluations to make sure Pacman doesnt get stuck in a loop of moves
    return gstate.score



class MultiAlphabetaAgent(agents.AdversarialAgent):
    def move(self, gstate):
        # Initial values of alpha and beta will be minus and plus infinity respectively.
        score, move = self.alpha_score(gstate, float('-inf'), float('inf'), 0, self.depth)
        return move

    # Pacman is the maximizer:
    def alpha_score(self, state, alpha, beta, agent_number, depth):
        # Once we've reached this state we're done here.
        if state.win or state.loss:
            return self.evaluate(state), 'none'

        # Initially set the score to minus infinity.
        score = float('-inf')

        # Gather the legal moves of Pacman.
        moves = list(state.legal_moves_id(agent_number))
        # Initiate the best_moves variable (with the first possible move).
        best_move = moves[0]

        # For all the moves it has collected:
        for move in moves:
            former_score = score  # save the old score.
            succ_gstate = state.successor(agent_number, move)  # get the successor state by applying this move.

            # If the game finishes or all leaf nodes.
            if succ_gstate.win or succ_gstate.loss or depth == 0:
                score = max(score, self.evaluate(succ_gstate))  # get the max score of the leaf nodes.
            else:
                # Else move over to the ghosts.
                score = max(score, self.beta_score(succ_gstate, alpha, beta, agent_number + 1, depth))

            if score > beta:  # Check the ability to prune.
                return score, move

            alpha = max(alpha, score)
            if score != former_score:
                best_move = move  # Save the best move out of the pruning process.
        return score, best_move

    # Ghosts are the minimizer:
    def beta_score(self, state, alpha, beta, agent_number, depth):
        # Once we've reached this state we're done here.
        if state.win or state.loss:
            return self.evaluate(state), 'none'

        score = float('inf')
        moves = state.legal_moves_id(agent_number)
        has_decremented = False

        for move in moves:
            succ_gstate = state.successor(agent_number, move)
            if depth == 0 or succ_gstate.win or succ_gstate.loss:
                score = min(score, self.evaluate(succ_gstate))
            # Else if this is the last agent (ghost) in the list:
            elif agent_number == (len(state.agents) - 1):
                # We don't want to decrement the depth of the same level more than once, so we use has_decremented.
                if not has_decremented:
                    depth -= 1  # Decrement the depth.
                    has_decremented = True
                if depth == 0:  # If we're at the deepest level check the minimum value of these successors.
                    score = min(score, self.evaluate(succ_gstate))
                else:
                    score = min(score, self.alpha_score(succ_gstate, alpha, beta, 0, depth)[0])

            else:
                score = min(score, self.beta_score(succ_gstate, alpha, beta, agent_number + 1, depth))
            if score < alpha:  # Checking pruning again.
                return score

            beta = min(beta, score)

        return score
