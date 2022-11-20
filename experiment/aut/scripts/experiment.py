import csv
from multiprocessing import Pool
import os
import subprocess
import networkmgmt
import sys

# settings
POOL_SIZE = 7
MEASUREMENTS_PER_TIMER = 1
TIMERS = 1
DEFAULT_SCENARIO_TO_TEST = 'scenario_packetloss.csv'
ALGORITHMS_TO_TEST = 'algorithms.csv'
MAIN_DIR = 'results'
ROW_NAMES = [0, 0.25, 0.5, 1, 1.5, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]

# prepare arrays
algorithmlist = []
algorithm_class_descriptions = []
scenariodescription = []

# runs given process
def run_subprocess(command, working_dir='.', expected_returncode=0):
    result = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=working_dir
    )
    #if (result.stderr):
    #    print(result.stderr)
    #assert result.returncode == expected_returncode
    return result.stdout.decode('utf-8')

# creates certificates to be used during handshake
def run_setup(sig_alg):
    command = [
        'sh', 'scripts/setup.sh', sig_alg
    ]
    run_subprocess(command)
    print("Created certificates using " + sig_alg)
    print("Signature OK")
    return

# prepares for next iteration with new certificates
def run_teardown():
    command = [
        'sh', 'scripts/teardown.sh'
    ]
    run_subprocess(command)
    return

# do TLS handshake (s_timer.c)
def time_handshake(sig_alg, measurements):
    command = [
        'ip', 'netns', 'exec', 'cli_ns',
        './s_timer.o', 'prime256v1', str(measurements)
    ]
    result = run_subprocess(command)
    return [float(i) for i in result.strip().split(',')]

# run timers
def run_timers(sig_alg, timer_pool):
    results_nested = timer_pool.starmap(time_handshake, [(sig_alg, MEASUREMENTS_PER_TIMER)] * TIMERS)
    return [item for sublist in results_nested for item in sublist]

# read algorithms.csv
def read_algorithms():
    if len(algorithmlist) > 0:
            return
    with open(ALGORITHMS_TO_TEST) as csv_file:
	    algor_classes = csv.reader(csv_file, delimiter=',')
	    for algor_class in algor_classes:
		    algorithms_of_certain_class = []
		    for algorithm in algor_class:
		            algorithms_of_certain_class.append(algorithm)
		    algorithm_class_descriptions.append(algorithms_of_certain_class.pop(0))
		    algorithmlist.append(algorithms_of_certain_class)
    return

# read handed scenario files
def read_testscenario(name_of_scenariofile):
    with open(name_of_scenariofile) as csv_file:
        network_scenario = csv.reader(csv_file, delimiter=',')
        for paramset in network_scenario:
            network_paramset = []
            for param in paramset:
                    network_paramset.append(param)
            paramsets.append(network_paramset)
        scenariodescription.append(paramsets[0][0])
        paramsets.pop(0)
    return

# creates directories if needed
def make_dirs():
    if not os.path.exists(MAIN_DIR):
        os.makedirs(MAIN_DIR)
    directory = '{}/{}'.format(MAIN_DIR, scenariodescription[0])
    for algor_class in algorithm_class_descriptions:
        if not os.path.exists('{}/{}'.format(directory, algor_class)):
            os.makedirs('{}/{}'.format(directory, algor_class))
    return directory

# prepare for handshake
def setup(name_of_scenariofile):

    read_testscenario(name_of_scenariofile)
    return make_dirs()

# MAIN #################################################################################################################

timer_pool = Pool(processes=POOL_SIZE)

scenariofiles = []
# Check for handed scenarios
if len(sys.argv) > 1:
        for i in range (1, len(sys.argv)):
                print(sys.argv[i])
                scenariofiles.append(sys.argv[i])
else:
        scenariofiles.append(DEFAULT_SCENARIO_TO_TEST)

index = 0

read_algorithms()
for algorithmclass in algorithmlist:
    for sig_alg in algorithmclass:

        run_setup(sig_alg)

        for scenariofile in scenariofiles:
                paramsets = []
                directory = setup(scenariofile)



                # set network parameters of scenario
                for paramset in paramsets:





                                            # To get actual (emulated) RTT
                                            networkmgmt.change_qdisc('srv_ns', 'srv_ve', 0, paramsets[0][2], 0, 0, 0, 0,
                                                                     paramsets[0][7])
                                            networkmgmt.change_qdisc('cli_ns', 'cli_ve', 0, paramsets[0][9], 0, 0, 0, 0,
                                                                     paramsets[0][14])
                                            rtt_str = networkmgmt.get_rtt_ms()

                                            networkmgmt.change_qdisc('srv_ns', 'srv_ve', paramset[1], paramset[2], paramset[3],
                                                                     paramset[4], paramset[5], paramset[6], paramset[7])
                                            networkmgmt.change_qdisc('cli_ns', 'cli_ve', paramset[8], paramset[9], paramset[10],
                                                                     paramset[11], paramset[12], paramset[13], paramset[14])

                                            print('{}/{}/{}.csv'.format(directory, algorithm_class_descriptions[index], sig_alg))
                                            with open('{}/{}/{}.csv'.format(directory, algorithm_class_descriptions[index], sig_alg),'a') as out:
                                                    csv_out = csv.writer(out)
                                                    result = run_timers(sig_alg, timer_pool)
                                                    result.insert(0, '{}'.format(ROW_NAMES[index]))
                                                    csv_out.writerow(result)




                scenariodescription.pop(0)
        run_teardown()
    index = index + 1

timer_pool.close()
timer_pool.join()
