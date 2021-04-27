"""
Visualize a genome.
"""

from __future__ import print_function
import os
import neat
from testing import visualize
import _pickle as pickle

def run(config_file):
    # Load configuration.
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)

    # Show output of the most fit genome against training data.
    genomeFile = '12_contestLevel0_3_93.p'
    genome = pickle.load(open(genomeFile, 'rb'))

    winner_net = neat.nn.FeedForwardNetwork.create(genome, config)

    node_names = {-1:'UP', -2: 'DOWN', -3: 'RIGHT', -4: 'LEFT',
                  -5: 'ghostx', -6: 'ghosty', -7: "ghostdistance",
                  -8: 'dotx', -9: 'doty',

                  0:'PressUP', 1: 'PressDOWN', 2: 'PressRIGHT', 3: 'PressLEFT'}
    visualize.draw_net(config, genome, True, node_names=node_names)

if __name__ == '__main__':
    # Determine path to configuration file. This path manipulation is
    # here so that the script will run successfully regardless of the
    # current working directory.
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config')
    run(config_path)