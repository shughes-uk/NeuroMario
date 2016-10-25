import os
from mariobot import MarioInterface
from neat import nn, population, statistics

mario_interface = MarioInterface()

def eval_fitness(genomes):
    for g in genomes:
        print("Testing {0}".format(g.ID))
        net = nn.create_feed_forward_phenotype(g)
        max_x = 0
        updates_since_last_max = 0
        while not mario_interface.mario_dead and updates_since_last_max < 15:
            inputs = list(mario_interface.tiles)
            inputs.append(mario_interface.mariox)
            outputs = net.serial_activate(inputs)
            if mario_interface.mariox > max_x:
                max_x = mario_interface.mariox
                updates_since_last_max = 0
            else:
                updates_since_last_max += 1
            mario_interface.joypad = outputs
            mario_interface.update()
        g.fitness = max_x
        print("Fitness {0}".format(g.fitness))
        mario_interface.reset()


local_dir = os.path.dirname(__file__)
config_path = os.path.join(local_dir, 'neuromario_neat.cfg')
pop = population.Population(config_path)
pop.run(eval_fitness, 300)

# Log statistics.
statistics.save_stats(pop.statistics)
statistics.save_species_count(pop.statistics)
statistics.save_species_fitness(pop.statistics)

print('Number of evaluations: {0}'.format(pop.total_evaluations))

# Show output of the most fit genome against training data.
winner = pop.statistics.best_genome()
print('\nBest genome:\n{!s}'.format(winner))
print('\nOutput:')
winner_net = nn.create_feed_forward_phenotype(winner)
