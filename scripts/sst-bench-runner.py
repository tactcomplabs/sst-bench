#!/usr/bin/env python3

#
# Copyright (C) 2017-2025 Tactical Computing Laboratories, LLC
# All Rights Reserved
# contact@tactcomplabs.com
#
# See LICENSE in the top level directory for licensing details
#
# sst-bench-runner.py
#
# Wrapper around sst that captures timing info and emits NDJSON.
# Designed for CTest integration: passes through SST output so
# "Simulation is complete" is visible for PASS_REGULAR_EXPRESSION,
# and emits a single NDJSON line with timing metrics for Logstash.
#

import argparse
import json
import os
import platform
import re
import socket
import subprocess
import sys
from datetime import datetime, timezone

# Add scripts directory to path for timing_tree_parser
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from timing_tree_parser import parse_timing_output, extract_key_metrics


def get_sst_version():
    try:
        result = subprocess.run(['sst', '--version'], capture_output=True, text=True)
        match = re.search(r'(\d+\.\d+\.\d+)', result.stdout + result.stderr)
        return match.group(1) if match else "unknown"
    except Exception:
        return "unknown"


def main():
    parser = argparse.ArgumentParser(description="SST benchmark test runner")
    parser.add_argument("config", help="SST config file path")
    parser.add_argument("--add-lib-path", required=True, help="SST library path")
    parser.add_argument("--topology", default="unknown", help="Topology name")
    parser.add_argument("--num-comps", type=int, default=0, help="Number of components")
    parser.add_argument("--config-type", default="unknown", help="Config format (json/python)")
    args = parser.parse_args()

    cmd = [
        'sst', '-v', '--print-timing-info=10',
        f'--add-lib-path={args.add_lib_path}',
        args.config
    ]

    # Capture stdout so we can parse timing info from it, then pass it through.
    # SST writes both "Simulation is complete" and the timing tree to stdout.
    result = subprocess.run(cmd, capture_output=True, text=True)

    # Pass through ALL output immediately so CTest sees "Simulation is complete"
    if result.stdout:
        print(result.stdout, end='', flush=True)
    if result.stderr:
        print(result.stderr, end='', file=sys.stderr, flush=True)

    # Parse timing from combined output and emit NDJSON
    try:
        combined = (result.stdout or '') + (result.stderr or '')
        tree = parse_timing_output(combined)
        metrics = extract_key_metrics(tree)
    except Exception:
        metrics = {}

    record = {
        "@timestamp": datetime.now(timezone.utc).isoformat(),
        "benchmark": "parser-bench",
        "hostname": socket.gethostname(),
        "platform": f"{platform.system().lower()}-{platform.machine()}",
        "sst_version": get_sst_version(),
        "config_type": args.config_type,
        "topology": args.topology,
        "num_components": args.num_comps,
        "exit_code": result.returncode,
        "total_duration_sec": metrics.get('total_duration_sec', 0.0),
        "total_memory_gb": metrics.get('total_memory_gb', 0.0),
        "build_duration_sec": metrics.get('build_duration_sec', 0.0),
        "build_memory_mb": metrics.get('build_memory_mb', 0.0),
        "graph_processing_duration_sec": metrics.get('graph_processing_duration_sec', 0.0),
        "model_generation_duration_sec": metrics.get('model_generation_duration_sec', 0.0),
        "model_execution_duration_sec": metrics.get('model_execution_duration_sec', 0.0),
        "execute_duration_sec": metrics.get('execute_duration_sec', 0.0),
        "run_duration_sec": metrics.get('run_duration_sec', 0.0),
    }

    # Emit NDJSON line — this appears in Jenkins console and flows to Logstash
    print(f"PARSER_BENCH_RESULT:{json.dumps(record)}", flush=True)

    sys.exit(result.returncode)


if __name__ == '__main__':
    main()
