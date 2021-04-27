"""
This file contains code for actually running a game of Pacman.
"""

import collections
import time
from typing import List

from pacman import agents, array, displays, gamestate, tech_util

# some constants are defined here that have to do with timeouts
PREPARE_TIMEOUT = 15  # seconds
MOVE_TIMEOUT = 1 # seconds
MOVE_WARNING = 0.2 # seconds
MAX_WARNINGS = 3   # times


def run_game(layout: array.Array, all_agents: List[agents.Agent], display: displays.Display, genome, config,
             speed: float = 1, timeouts: bool = True):
    """
    Run a game of pacman.
    :param layout: layout to use
    :param all_agents: list of agents to use, first of which is Pacman
    :param display: the display to use
    :param speed: the speed to use
    :param timeouts: whether to use agent move timeouts
    """
    # create initial gamestate
    gstate = gamestate.Gamestate(layout)

    # let agents prepare
    for index, agent in enumerate(all_agents):
        if timeouts:
            agent_prepare_timeout(agent, gstate)
        elif index is 0:
            agent.prepare(gstate.copy, genome, config)
        else:  # pass the genome here?
            agent.prepare(gstate.copy)

    # initialise the display
    pacman: agents.PacmanAgent = all_agents[0]
    display.initialise(gstate.copy, pacman.cell_values)
    display.show(gstate.copy)

    # initialise timeout warning counter
    timeout_warnings = collections.Counter()
    timeit = None
    stats = GameStats()

    # main game loop
    while not gstate.gameover:
        # ask each agent that can move for their next move and apply it to the gamestate
        for agent in all_agents:
            if gstate.gameover: # game should stop immediately when win or loss occurs
                break
            
            if gstate.can_move(agent.id):
                if timeouts:
                    move, movetime = agent_move_timeout(agent, gstate, timeout_warnings)
                else:
                    with tech_util.timeit() as timeit:
                        move = agent.move(gstate.copy)  # gets called every turn.
                    movetime = timeit.t
                gstate.apply_move(agent.id, move)
        
        stats.register_move(movetime)
        gstate.tick()
        display.show(gstate.copy)
        time.sleep(display.preferred_timedelta / speed)
    
    stats.register_game(gstate.score, gstate.win, timeout_warnings[0] >= MAX_WARNINGS)

    # reset display
    display.reset()

    return gstate.copy, stats


def agent_prepare_timeout(agent: agents.Agent, gstate: gamestate.Gamestate):
    """
    Let agent prepare, while applying timeouts
    """
    try:
        with tech_util.timeout(PREPARE_TIMEOUT):
            agent.prepare(gstate.copy)
    except tech_util.TimeoutException:
        gstate.destroy(agent.id)
        print(f'WARNING! agent {agent.id} reached prepare timeout of {PREPARE_TIMEOUT} seconds and was destroyed')


def agent_move_timeout(agent: agents.Agent, gstate: gamestate.Gamestate, timeout_warnings: collections.Counter):
    """
    Let agent calculate their next move, while applying timeouts
    """
    move = None
    timeit = None
    try:
        with tech_util.timeit() as timeit, tech_util.timeout(MOVE_TIMEOUT):
            move = agent.move(gstate.copy)
    except tech_util.TimeoutException:
        timeout_warnings[agent.id] += MAX_WARNINGS
        gstate.destroy(agent.id)
        print(f'WARNING! agent {agent.id} reached move timeout of {MOVE_TIMEOUT} seconds and was destroyed')
    finally:
        if timeit and timeit.t >= MOVE_WARNING:
            timeout_warnings[agent.id] += 1
            print(f'WARNING! agent {agent.id} took more than {MOVE_WARNING} seconds to move, '
                  f'agent now has {timeout_warnings[agent.id]} warning(s)')
            if timeout_warnings[agent.id] >= MAX_WARNINGS:
                gstate.destroy(agent.id)
                print(f'WARNING! agent {agent.id} was warned {MAX_WARNINGS} times and was destroyed')
    
    return move, timeit.t

class GameStats:
    def __init__(self, num_games=0, num_moves=0, sum_score=0, sum_times=0, num_wins=0, num_timeouts=0):
        self.num_games = num_games
        self.num_moves = num_moves
        self.sum_score = sum_score
        self.sum_times = sum_times
        self.num_wins  = num_wins
        self.timeouts  = num_timeouts
    
    def register_move(self, time):
        self.num_moves += 1
        self.sum_times += time
        
    def register_game(self, score, win, timeout):
        self.num_games += 1
        self.sum_score += score
        self.num_wins += win
        self.timeouts += timeout
        
    def __add__(self, other):
        if not isinstance(other, GameStats): 
            raise TypeError('You can only add a GameStats to another GameStats')
        return GameStats(self.num_games + other.num_games,
                         self.num_moves + other.num_moves,
                         self.sum_score + other.sum_score,
                         self.sum_times + other.sum_times,
                         self.num_wins  + other.num_wins,
                         self.timeouts  + other.timeouts)
        
