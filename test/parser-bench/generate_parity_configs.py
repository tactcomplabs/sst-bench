#!/usr/bin/env python3

#
# Copyright (C) 2017-2025 Tactical Computing Laboratories, LLC
# All Rights Reserved
# contact@tactcomplabs.com
#
# See LICENSE in the top level directory for licensing details
#
# generate_parity_configs.py
#
# Generate JSON equivalents of noodle-test1/2/3 for parser parity testing
#

"""
Generate JSON configuration files that are functionally equivalent
to the hand-written noodle-test1.py, noodle-test2.py, and noodle-test3.py
Python SDL configurations.

Usage:
    python3 generate_parity_configs.py <output_dir>
"""

import json
import os
import sys


def make_json_config(components, links):
    """Build an SST JSON config dict from components and links."""
    config = {
        'program_options': {
            'timebase': '1 ps',
            'partitioner': 'sst.linear',
            'timeVortex': 'sst.timevortex.priority_queue',
            'checkpoint-sim-period': '',
            'checkpoint-wall-period': ''
        },
        'statistics_options': {
            'statisticOutput': 'sst.statOutputConsole'
        },
        'components': components,
        'links': links
    }
    return config


def make_link(name, comp1, port1, comp2, port2, latency='1us'):
    """Build a link dict in SST JSON format."""
    return {
        'name': name,
        'noCut': False,
        'nonlocal': False,
        'left': {
            'component': comp1,
            'port': port1,
            'latency': latency
        },
        'right': {
            'component': comp2,
            'port': port2,
            'latency': latency
        }
    }


def generate_noodle_test1():
    """
    JSON equivalent of noodle-test1.py:
    2 components, 1 port each, simple pair connection.
    """
    params = {
        'verbose': '0',
        'clockFreq': '1GHz',
        'numPorts': '1',
        'msgPerClock': '1',
        'bytesPerClock': '1',
        'portsPerClock': '1',
        'clocks': '100000',
        'rngSeed': '3131'
    }
    components = [
        {'name': 'n0', 'type': 'noodle.Noodle', 'params': dict(params)},
        {'name': 'n1', 'type': 'noodle.Noodle', 'params': dict(params)},
    ]
    links = [
        make_link('link0', 'n0', 'port0', 'n1', 'port0', '1us'),
    ]
    return make_json_config(components, links)


def generate_noodle_test2():
    """
    JSON equivalent of noodle-test2.py:
    2 components, 8 ports each, non-uniform params per component.
    """
    base = {
        'verbose': '0',
        'clockFreq': '1GHz',
        'numPorts': '8',
        'clocks': '100000',
        'rngSeed': '3131'
    }
    params_n0 = dict(base, msgPerClock='3', bytesPerClock='4', portsPerClock='3')
    params_n1 = dict(base, msgPerClock='9', bytesPerClock='7', portsPerClock='5')

    components = [
        {'name': 'n0', 'type': 'noodle.Noodle', 'params': params_n0},
        {'name': 'n1', 'type': 'noodle.Noodle', 'params': params_n1},
    ]
    links = [
        make_link(f'link{i}', 'n0', f'port{i}', 'n1', f'port{i}', '1us')
        for i in range(8)
    ]
    return make_json_config(components, links)


def generate_noodle_test3():
    """
    JSON equivalent of noodle-test3.py:
    2 components, 1 port each, with randClockRange instead of clockFreq.
    """
    base = {
        'verbose': '0',
        'numPorts': '1',
        'msgPerClock': '1',
        'bytesPerClock': '1',
        'portsPerClock': '1',
        'clocks': '100000',
        'rngSeed': '3131'
    }
    params_n0 = dict(base, randClockRange='1-3')
    params_n1 = dict(base, randClockRange='5-9')

    components = [
        {'name': 'n0', 'type': 'noodle.Noodle', 'params': params_n0},
        {'name': 'n1', 'type': 'noodle.Noodle', 'params': params_n1},
    ]
    links = [
        make_link('link0', 'n0', 'port0', 'n1', 'port0', '1us'),
    ]
    return make_json_config(components, links)


def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <output_dir>", file=sys.stderr)
        sys.exit(1)

    output_dir = sys.argv[1]
    os.makedirs(output_dir, exist_ok=True)

    tests = {
        'noodle-test1.json': generate_noodle_test1,
        'noodle-test2.json': generate_noodle_test2,
        'noodle-test3.json': generate_noodle_test3,
    }

    for filename, generator in tests.items():
        path = os.path.join(output_dir, filename)
        config = generator()
        with open(path, 'w') as f:
            json.dump(config, f, indent=2)
        print(f"Generated {path}", file=sys.stderr)


if __name__ == '__main__':
    main()
