#!/usr/bin/env python3

#
# Copyright (C) 2017-2025 Tactical Computing Laboratories, LLC
# All Rights Reserved
# contact@tactcomplabs.com
#
# See LICENSE in the top level directory for licensing details
#
# config_generator.py
#
# Generate SST configurations on-the-fly in both JSON and Python SDL formats
#

"""
Generate SST configurations for benchmarking parser performance.

Supports two output formats:
- Python SDL: Traditional SST Python configuration files
- JSON: SST's native JSON configuration format

Supports topologies:
- Chain: Sequential ring A -> B -> C -> D -> A
- Fully-connected: Every component connected to every other (N*(N-1)/2 links)
"""

import argparse
import json
import sys
from typing import List, Tuple, Dict, Any


def generate_chain_topology(num_comps: int, ports_per_comp: int,
                            params: Dict[str, Any]) -> Tuple[List[Dict], List[Dict]]:
    """
    Generate a chain/ring topology where components form a ring.
    Each component uses port0 to connect to the previous component
    and port1 to connect to the next component (for ports_per_comp >= 2).
    For single-port components, creates simple pairs.

    Args:
        num_comps: Number of components
        ports_per_comp: Number of ports per component
        params: Component parameters

    Returns:
        Tuple of (components list, links list)
    """
    components = []
    links = []

    for i in range(num_comps):
        comp = {
            'name': f'n{i}',
            'type': 'noodle.Noodle',
            'params': {
                'verbose': params.get('verbose', 0),
                'clockFreq': params.get('clock_freq', '1GHz'),
                'numPorts': ports_per_comp,
                'msgPerClock': params.get('msgs_per_clock', 1),
                'bytesPerClock': params.get('bytes_per_clock', 8),
                'portsPerClock': params.get('ports_per_clock', 1),
                'clocks': params.get('clocks', 10000),
                'rngSeed': params.get('rng_seed', 31337)
            }
        }
        components.append(comp)

    link_id = 0

    if ports_per_comp == 1:
        # Single port: create pairs of components connected together
        # Each pair connects their single ports to each other
        for i in range(0, num_comps - 1, 2):
            link = {
                'name': f'link{link_id}',
                'comp1': f'n{i}',
                'port1': 'port0',
                'comp2': f'n{i+1}',
                'port2': 'port0',
                'latency': params.get('link_latency', '1us')
            }
            links.append(link)
            link_id += 1
        # If odd number of components, connect last to first
        if num_comps % 2 == 1 and num_comps > 1:
            link = {
                'name': f'link{link_id}',
                'comp1': f'n{num_comps-1}',
                'port1': 'port0',
                'comp2': f'n0',
                'port2': 'port0',
                'latency': params.get('link_latency', '1us')
            }
            links.append(link)
    else:
        # Multiple ports: create a ring using port0 and port1
        # n0.port1 -> n1.port0, n1.port1 -> n2.port0, ..., nN.port1 -> n0.port0
        for i in range(num_comps):
            next_i = (i + 1) % num_comps
            link = {
                'name': f'link{link_id}',
                'comp1': f'n{i}',
                'port1': 'port1',
                'comp2': f'n{next_i}',
                'port2': 'port0',
                'latency': params.get('link_latency', '1us')
            }
            links.append(link)
            link_id += 1

        # Connect remaining ports in pairs within each component's neighbors
        # For ports 2,3,4,... connect to corresponding ports on adjacent components
        for p in range(2, ports_per_comp):
            for i in range(num_comps):
                # Connect to next component's same port number
                next_i = (i + 1) % num_comps
                # Only create link once (avoid duplicates)
                if i < next_i or (i == num_comps - 1 and next_i == 0):
                    link = {
                        'name': f'link{link_id}',
                        'comp1': f'n{i}',
                        'port1': f'port{p}',
                        'comp2': f'n{next_i}',
                        'port2': f'port{p}',
                        'latency': params.get('link_latency', '1us')
                    }
                    links.append(link)
                    link_id += 1

    return components, links



def generate_fully_connected_topology(num_comps: int, ports_per_comp: int,
                                       params: Dict[str, Any]) -> Tuple[List[Dict], List[Dict]]:
    """
    Generate a fully-connected topology where every component connects
    to every other component. Creates N*(N-1)/2 links.

    Each component needs (N-1) ports to connect to all others.

    Args:
        num_comps: Number of components
        ports_per_comp: Number of ports per component (overridden to N-1)
        params: Component parameters

    Returns:
        Tuple of (components list, links list)
    """
    # Each component needs (num_comps - 1) ports
    actual_ports = num_comps - 1 if num_comps > 1 else 1

    components = []
    links = []

    # Create components
    for i in range(num_comps):
        comp = {
            'name': f'n{i}',
            'type': 'noodle.Noodle',
            'params': {
                'verbose': params.get('verbose', 0),
                'clockFreq': params.get('clock_freq', '1GHz'),
                'numPorts': actual_ports,
                'msgPerClock': params.get('msgs_per_clock', 1),
                'bytesPerClock': params.get('bytes_per_clock', 8),
                'portsPerClock': params.get('ports_per_clock', 1),
                'clocks': params.get('clocks', 10000),
                'rngSeed': params.get('rng_seed', 31337)
            }
        }
        components.append(comp)

    # Track which port to use next for each component
    next_port = [0] * num_comps

    link_id = 0
    latency = params.get('link_latency', '1us')

    # Connect every pair of components
    for i in range(num_comps):
        for j in range(i + 1, num_comps):
            link = {
                'name': f'link{link_id}',
                'comp1': f'n{i}',
                'port1': f'port{next_port[i]}',
                'comp2': f'n{j}',
                'port2': f'port{next_port[j]}',
                'latency': latency
            }
            links.append(link)
            link_id += 1
            next_port[i] += 1
            next_port[j] += 1

    return components, links


def write_python_sdl(components: List[Dict], links: List[Dict], output_path: str):
    """
    Write a Python SDL configuration file.

    Args:
        components: List of component definitions
        links: List of link definitions
        output_path: Path to output file
    """
    lines = [
        '#',
        '# Copyright (C) 2017-2025 Tactical Computing Laboratories, LLC',
        '# All Rights Reserved',
        '# contact@tactcomplabs.com',
        '#',
        '# See LICENSE in the top level directory for licensing details',
        '#',
        '# Auto-generated SST configuration for parser benchmarking',
        '#',
        '',
        'import sst',
        '',
        '# Component definitions',
    ]

    # Write component definitions
    for comp in components:
        lines.append(f'{comp["name"]} = sst.Component("{comp["name"]}", "{comp["type"]}")')
        lines.append(f'{comp["name"]}.addParams({{')
        params = comp['params']
        param_lines = []
        for key, value in params.items():
            if isinstance(value, str):
                param_lines.append(f'    "{key}": "{value}"')
            else:
                param_lines.append(f'    "{key}": {value}')
        lines.append(',\n'.join(param_lines))
        lines.append('})')
        lines.append('')

    # Write link definitions
    lines.append('# Link definitions')
    for link in links:
        lines.append(f'{link["name"]} = sst.Link("{link["name"]}")')
        lines.append(f'{link["name"]}.connect(')
        lines.append(f'    ({link["comp1"]}, "{link["port1"]}", "{link["latency"]}"),')
        lines.append(f'    ({link["comp2"]}, "{link["port2"]}", "{link["latency"]}")')
        lines.append(')')
        lines.append('')

    lines.append('# EOF')

    with open(output_path, 'w') as f:
        f.write('\n'.join(lines))


def write_json_config(components: List[Dict], links: List[Dict], output_path: str):
    """
    Write an SST JSON configuration file.

    Args:
        components: List of component definitions
        links: List of link definitions
        output_path: Path to output file
    """
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
        'components': [],
        'links': []
    }

    # Add components
    for comp in components:
        json_comp = {
            'name': comp['name'],
            'type': comp['type'],
            'params': {k: str(v) for k, v in comp['params'].items()}
        }
        config['components'].append(json_comp)

    # Add links
    for link in links:
        json_link = {
            'name': link['name'],
            'noCut': False,
            'nonlocal': False,
            'left': {
                'component': link['comp1'],
                'port': link['port1'],
                'latency': link['latency']
            },
            'right': {
                'component': link['comp2'],
                'port': link['port2'],
                'latency': link['latency']
            }
        }
        config['links'].append(json_link)

    with open(output_path, 'w') as f:
        json.dump(config, f, indent=2)


def generate_config(num_comps: int, ports_per_comp: int, topology: str,
                    output_format: str, output_path: str, params: Dict[str, Any]):
    """
    Generate an SST configuration file.

    Args:
        num_comps: Number of components
        ports_per_comp: Number of ports per component
        topology: Topology type ('chain' or 'fully-connected')
        output_format: Output format ('json' or 'python')
        output_path: Path to output file
        params: Additional component parameters
    """
    # Generate topology
    if topology == 'chain':
        components, links = generate_chain_topology(num_comps, ports_per_comp, params)
    elif topology == 'fully-connected':
        components, links = generate_fully_connected_topology(num_comps, ports_per_comp, params)
    else:
        raise ValueError(f"Unknown topology: {topology}")

    # Write output
    if output_format == 'python':
        write_python_sdl(components, links, output_path)
    elif output_format == 'json':
        write_json_config(components, links, output_path)
    else:
        raise ValueError(f"Unknown format: {output_format}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog="config_generator.py",
        description="Generate SST configurations for parser benchmarking")

    parser.add_argument("--num-comps", type=int, required=True,
                        help="Number of components")
    parser.add_argument("--ports-per-comp", type=int, default=1,
                        help="Number of ports per component [1]")
    parser.add_argument("--topology", type=str,
                        choices=['chain', 'fully-connected'],
                        default='chain', help="Topology type [chain]")
    parser.add_argument("--format", type=str, choices=['json', 'python'],
                        default='python', help="Output format [python]")
    parser.add_argument("--output", "-o", type=str, required=True,
                        help="Output file path")

    # Component parameters
    parser.add_argument("--clock-freq", type=str, default="1GHz",
                        help="Component clock frequency [1GHz]")
    parser.add_argument("--clocks", type=int, default=10000,
                        help="Number of clock cycles [10000]")
    parser.add_argument("--rng-seed", type=int, default=31337,
                        help="RNG seed for reproducibility [31337]")
    parser.add_argument("--msgs-per-clock", type=int, default=1,
                        help="Messages per clock [1]")
    parser.add_argument("--bytes-per-clock", type=int, default=8,
                        help="Bytes per clock [8]")
    parser.add_argument("--ports-per-clock", type=int, default=1,
                        help="Ports to send per clock [1]")
    parser.add_argument("--link-latency", type=str, default="1us",
                        help="Link latency [1us]")
    parser.add_argument("--verbose", type=int, default=0,
                        help="Verbosity level [0]")

    args = parser.parse_args()

    params = {
        'clock_freq': args.clock_freq,
        'clocks': args.clocks,
        'rng_seed': args.rng_seed,
        'msgs_per_clock': args.msgs_per_clock,
        'bytes_per_clock': args.bytes_per_clock,
        'ports_per_clock': args.ports_per_clock,
        'link_latency': args.link_latency,
        'verbose': args.verbose
    }

    generate_config(
        num_comps=args.num_comps,
        ports_per_comp=args.ports_per_comp,
        topology=args.topology,
        output_format=args.format,
        output_path=args.output,
        params=params
    )

    print(f"Generated {args.format} config with {args.num_comps} components, "
          f"{args.topology} topology -> {args.output}", file=sys.stderr)
