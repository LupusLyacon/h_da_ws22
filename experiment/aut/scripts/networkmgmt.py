from multiprocessing import Pool
import os
import subprocess

def run_subprocess(command, working_dir='.', expected_returncode=0):
    result = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=working_dir
    )
    if(result.stderr):
        print(result.stderr)
    assert result.returncode == expected_returncode
    return result.stdout.decode('utf-8')

def change_qdisc(ns, dev, pkt_loss, delay, jitter, duplicate, corrupt, reorder, rate):

    command = [
        'ip', 'netns', 'exec', ns,
        'tc', 'qdisc', 'change',
        'dev', dev, 'root', 'netem',
        'limit', '1000'
    ]

    if pkt_loss != 0:
        command.append('loss')
        command.append('{0}%'.format(pkt_loss))

    if duplicate != 0:
        command.append('duplicate')
        command.append('{0}%'.format(duplicate))

    if corrupt != 0:
        command.append('corrupt')
        command.append('{0}%'.format(corrupt))

    if reorder != 0:
        command.append('reorder')
        command.append('{0}%'.format(reorder))

    command.append('delay')
    command.append(delay)

    if jitter != 0:
        command.append(jitter)
        # command.append('25%')

    command.append('rate')
    command.append('{0}mbit'.format(rate))

    print(" > " + " ".join(command))
    run_subprocess(command)

def get_rtt_ms():
    command = [
        'ip', 'netns', 'exec', 'cli_ns',
        'ping', '10.0.0.1', '-c', '10'
    ]

    print(" > " + " ".join(command))
    result = run_subprocess(command)

    result_fmt = result.splitlines()[-1].split("/")
    return result_fmt[4].replace(".", "p")
