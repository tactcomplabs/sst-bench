#!/usr/bin/env python3

#
# Copyright (C) 2017-2025 Tactical Computing Laboratories, LLC
# All Rights Reserved
# contact@tactcomplabs.com
#
# See LICENSE in the top level directory for licensing details
#
# parser-bench.py
#
# Benchmark driver for comparing SST configuration parsing performance
# between JSON and Python SDL formats
#

"""
SST Parser Performance Benchmark Driver

Orchestrates benchmark runs and outputs Logstash-compatible NDJSON.

Usage:
    python parser-bench.py --comp-range 100,1000,5000 --topologies chain,fully-connected \
        --formats json,python --runs 3

Output: NDJSON (one JSON object per line) to stdout
"""

import argparse
import json
import os
import platform
import re
import shutil
import socket
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any

# Import local modules
from config_generator import generate_config
from timing_tree_parser import parse_timing_output, extract_key_metrics


def get_sst_version() -> str:
    """Get SST version from sst --version command."""
    try:
        result = subprocess.run(['sst', '--version'], capture_output=True, text=True)
        # Parse version from output (typically "SST-Core Version X.Y.Z")
        output = result.stdout + result.stderr
        match = re.search(r'(\d+\.\d+\.\d+)', output)
        if match:
            return match.group(1)
        return "unknown"
    except Exception:
        return "unknown"


def get_platform_info() -> str:
    """Get platform identifier string."""
    system = platform.system().lower()
    machine = platform.machine()
    return f"{system}-{machine}"


def run_sst_benchmark(config_path: str, timing_level: int = 10,
                      timeout: int = 3600) -> Dict[str, Any]:
    """
    Run SST with the given configuration and capture timing output.

    Args:
        config_path: Path to SST configuration file
        timing_level: Level for --print-timing-info (default 10)
        timeout: Maximum runtime in seconds (default 3600)

    Returns:
        Dictionary with timing metrics and exit info
    """
    cmd = ['sst', '-v', f'--print-timing-info={timing_level}', config_path]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout
        )

        # Parse timing output from stderr (SST writes timing info there)
        timing_output = result.stderr + result.stdout
        tree = parse_timing_output(timing_output)
        metrics = extract_key_metrics(tree)

        return {
            'metrics': metrics,
            'exit_code': result.returncode,
            'error': None if result.returncode == 0 else result.stderr[:500]
        }

    except subprocess.TimeoutExpired:
        return {
            'metrics': {},
            'exit_code': -1,
            'error': f"Timeout after {timeout} seconds"
        }
    except Exception as e:
        return {
            'metrics': {},
            'exit_code': -1,
            'error': str(e)
        }


def run_benchmark_suite(comp_range: List[int], topologies: List[str],
                        formats: List[str], runs: int, ports_per_comp: int,
                        clocks: int, rng_seed: int, output_dir: Optional[str],
                        timing_level: int, timeout: int):
    """
    Run the full benchmark suite and output NDJSON results.

    Args:
        comp_range: List of component counts to test
        topologies: List of topologies to test
        formats: List of formats to test
        runs: Number of runs per configuration
        ports_per_comp: Ports per component
        clocks: Clock cycles per component
        rng_seed: Base RNG seed
        output_dir: Directory for temporary config files
        timing_level: SST timing info level
        timeout: Timeout per run in seconds
    """
    # Get system info once
    hostname = socket.gethostname()
    platform_info = get_platform_info()
    sst_version = get_sst_version()

    # Create output directory if needed
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        work_dir = output_dir
        cleanup_dir = False
    else:
        work_dir = tempfile.mkdtemp(prefix='sst-parser-bench-')
        cleanup_dir = True

    try:
        # Run benchmarks
        for num_comps in comp_range:
            for topology in topologies:
                for config_format in formats:
                    for run_num in range(1, runs + 1):
                        # Generate config file
                        ext = '.py' if config_format == 'python' else '.json'
                        config_name = f"bench_{num_comps}_{topology}_{config_format}{ext}"
                        config_path = os.path.join(work_dir, config_name)

                        params = {
                            'clock_freq': '1GHz',
                            'clocks': clocks,
                            'rng_seed': rng_seed + run_num,
                            'msgs_per_clock': 1,
                            'bytes_per_clock': 8,
                            'ports_per_clock': 1,
                            'link_latency': '1us',
                            'verbose': 0
                        }

                        # Generate configuration
                        generate_config(
                            num_comps=num_comps,
                            ports_per_comp=ports_per_comp,
                            topology=topology,
                            output_format=config_format,
                            output_path=config_path,
                            params=params
                        )

                        # Run benchmark
                        result = run_sst_benchmark(
                            config_path=config_path,
                            timing_level=timing_level,
                            timeout=timeout
                        )

                        # Build output record
                        record = {
                            'timestamp': datetime.now(timezone.utc).isoformat(),
                            'hostname': hostname,
                            'platform': platform_info,
                            'sst_version': sst_version,
                            'config_type': config_format,
                            'topology': topology,
                            'num_components': num_comps,
                            'ports_per_comp': ports_per_comp,
                            'clocks': clocks,
                            'run_number': run_num,
                            'exit_code': result['exit_code'],
                            'error': result['error']
                        }

                        # Add timing metrics
                        metrics = result['metrics']
                        record['total_duration_sec'] = metrics.get('total_duration_sec', 0.0)
                        record['total_memory_gb'] = metrics.get('total_memory_gb', 0.0)
                        record['build_duration_sec'] = metrics.get('build_duration_sec', 0.0)
                        record['build_memory_mb'] = metrics.get('build_memory_mb', 0.0)
                        record['graph_processing_duration_sec'] = metrics.get('graph_processing_duration_sec', 0.0)
                        record['model_generation_duration_sec'] = metrics.get('model_generation_duration_sec', 0.0)
                        record['model_execution_duration_sec'] = metrics.get('model_execution_duration_sec', 0.0)
                        record['execute_duration_sec'] = metrics.get('execute_duration_sec', 0.0)
                        record['run_duration_sec'] = metrics.get('run_duration_sec', 0.0)

                        # Output NDJSON record
                        print(json.dumps(record))
                        sys.stdout.flush()

                        # Clean up config file if not keeping output
                        if cleanup_dir:
                            try:
                                os.remove(config_path)
                            except OSError:
                                pass

    finally:
        # Clean up temp directory
        if cleanup_dir:
            try:
                shutil.rmtree(work_dir)
            except OSError:
                pass


def parse_range_list(value: str) -> List[int]:
    """Parse a comma-separated list of integers."""
    return [int(x.strip()) for x in value.split(',')]


def parse_string_list(value: str) -> List[str]:
    """Parse a comma-separated list of strings."""
    return [x.strip() for x in value.split(',')]


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog="parser-bench.py",
        description="SST Parser Performance Benchmark Driver",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Single quick test
  python parser-bench.py --comp-range 100 --topologies chain --formats python --runs 1

  # Full benchmark suite
  python parser-bench.py --comp-range 100,500,1000,5000,10000 \\
      --topologies chain,fully-connected --formats json,python --runs 3

  # Save configs for debugging
  python parser-bench.py --comp-range 100 --topologies chain \\
      --formats python --runs 1 --output-dir /tmp/bench-configs
""")

    parser.add_argument("--comp-range", type=str, required=True,
                        help="Comma-separated list of component counts (e.g., '100,1000,5000')")
    parser.add_argument("--topologies", type=str, default="chain,fully-connected",
                        help="Comma-separated list of topologies: chain,fully-connected [chain,fully-connected]")
    parser.add_argument("--formats", type=str, default="json,python",
                        help="Comma-separated list of formats [json,python]")
    parser.add_argument("--runs", type=int, default=3,
                        help="Number of runs per configuration [3]")
    parser.add_argument("--ports-per-comp", type=int, default=1,
                        help="Ports per component [1]")
    parser.add_argument("--clocks", type=int, default=1000,
                        help="Clock cycles per component [1000]")
    parser.add_argument("--rng-seed", type=int, default=31337,
                        help="Base RNG seed [31337]")
    parser.add_argument("--output-dir", type=str,
                        help="Directory for config files (temp dir if not specified)")
    parser.add_argument("--timing-level", type=int, default=10,
                        help="SST timing info level [10]")
    parser.add_argument("--timeout", type=int, default=3600,
                        help="Timeout per run in seconds [3600]")

    args = parser.parse_args()

    # Parse list arguments
    comp_range = parse_range_list(args.comp_range)
    topologies = parse_string_list(args.topologies)
    formats = parse_string_list(args.formats)

    # Validate
    valid_topologies = ['chain', 'fully-connected']
    for t in topologies:
        if t not in valid_topologies:
            print(f"Error: Unknown topology '{t}'. Use one of: {', '.join(valid_topologies)}",
                  file=sys.stderr)
            sys.exit(1)

    for f in formats:
        if f not in ['json', 'python']:
            print(f"Error: Unknown format '{f}'. Use 'json' or 'python'.",
                  file=sys.stderr)
            sys.exit(1)

    # Run benchmark suite
    run_benchmark_suite(
        comp_range=comp_range,
        topologies=topologies,
        formats=formats,
        runs=args.runs,
        ports_per_comp=args.ports_per_comp,
        clocks=args.clocks,
        rng_seed=args.rng_seed,
        output_dir=args.output_dir,
        timing_level=args.timing_level,
        timeout=args.timeout
    )
