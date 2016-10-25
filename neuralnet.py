import os
from mariobot import MarioInterface
from neat import nn, population, statistics
from threading import Thread
emulator_clients = 10
clients = []
for x in range(0, emulator_clients):
    clients.append(MarioInterface(operating_port=9001+x))

def eval_fitness(genomes):
    worker_threads = []
    gpc = int(len(genomes)/emulator_clients)
    for n in range(0, emulator_clients):
        target_genomes = genomes[:gpc]
        genomes = genomes[gpc:]
        worker = Thread(target=test_genomes, args=[target_genomes, clients[n]])
        worker.daemon = True
        worker.start()
        worker_threads.append(worker)
    for worker_thread in worker_threads:
        worker_thread.join()

def test_genomes(genomes, mario_interface):
    for g in genomes:
        net = nn.create_feed_forward_phenotype(g)
        max_x = 0
        updates_since_last_max = 0
        # old_outputs = []
        while not mario_interface.mario_dead and updates_since_last_max < 10:
            inputs = list(mario_interface.tiles)
            inputs.append(mario_interface.mariox)
            outputs = [int(round(x)) for x in net.serial_activate(inputs)]
            if mario_interface.mariox > max_x:
                max_x = mario_interface.mariox
                updates_since_last_max = 0
            else:
                updates_since_last_max += 1
            mario_interface.joypad = outputs
            mario_interface.update()
            # if outputs != old_outputs:
            #     print("outputs changed to")
            #     print(outputs)
            #     pass
            # old_outputs = outputs
        g.fitness = max_x
        # print("Tested : {0} Fitness {1}".format(g.ID,g.fitness))
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
