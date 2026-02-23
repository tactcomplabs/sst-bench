#!/usr/bin/env python3

#
# Copyright (C) 2017-2025 Tactical Computing Laboratories, LLC
# All Rights Reserved
# contact@tactcomplabs.com
#
# See LICENSE in the top level directory for licensing details
#
# emit_ndjson.py
#
# Reads *.timing.json files produced by `sst --timing-info-json` and emits
# one PARSER_BENCH_RESULT:{json} NDJSON line per file to stdout.
# Designed to run as a CTest FIXTURES_CLEANUP test so Jenkins/Logstash
# captures the output after all parser-bench tests complete.
#

import argparse
import glob
import json
import os
import platform
import re
import socket
import subprocess
import sys
from datetime import datetime, timezone


def get_sst_version():
    try:
        result = subprocess.run(['sst', '--version'], capture_output=True, text=True)
        match = re.search(r'(\d+\.\d+\.\d+)', result.stdout + result.stderr)
        return match.group(1) if match else "unknown"
    except Exception:
        return "unknown"


# Filename pattern: parser-bench-<topology>-<size>-<format>.timing.json
# Parity pattern:   parser-bench-noodle-test<N>-json.timing.json
BENCH_RE = re.compile(
    r'^parser-bench-(.+)-(\d+)-(json|python)\.timing\.json$'
)
PARITY_RE = re.compile(
    r'^parser-bench-noodle-test(\d+)-(json)\.timing\.json$'
)


def parse_filename(basename):
    """Extract topology, num_components, and config_type from timing filename."""
    m = PARITY_RE.match(basename)
    if m:
        return "parity", 2, m.group(2)
    m = BENCH_RE.match(basename)
    if m:
        return m.group(1), int(m.group(2)), m.group(3)
    return None, None, None


def get_jenkins_metadata():
    """Collect Jenkins environment variables when running in a Jenkins build."""
    keys = ("BUILD_NUMBER", "BUILD_URL", "JOB_NAME", "BUILD_ID")
    return {k.lower(): os.environ[k] for k in keys if k in os.environ}


def build_record(timing_file, hostname, plat, sst_version, jenkins_meta):
    """Read a timing JSON file and build an NDJSON record."""
    basename = os.path.basename(timing_file)
    topology, num_components, config_type = parse_filename(basename)
    if topology is None:
        return None

    with open(timing_file) as f:
        data = json.load(f)

    info = data.get("timing-info", {})

    max_rss_kb = info.get("global_max_rss", 0)
    total_memory_gb = max_rss_kb / 1048576.0

    record = {
        "@timestamp": datetime.now(timezone.utc).isoformat(),
        "benchmark": "parser-bench",
        "hostname": hostname,
        "platform": plat,
        "sst_version": sst_version,
        "config_type": config_type,
        "topology": topology,
        "num_components": num_components,
        "exit_code": 0,
        "total_duration_sec": info.get("max_total_time", 0.0),
        "total_memory_gb": total_memory_gb,
        "build_duration_sec": info.get("max_build_time", 0.0),
        "build_memory_mb": 0.0,
        "graph_processing_duration_sec": 0.0,
        "model_generation_duration_sec": 0.0,
        "model_execution_duration_sec": 0.0,
        "execute_duration_sec": 0.0,
        "run_duration_sec": info.get("max_run_time", 0.0),
    }
    record.update(jenkins_meta)
    return record


def main():
    parser = argparse.ArgumentParser(
        description="Emit NDJSON from SST timing JSON files"
    )
    parser.add_argument(
        "--timing-dir", required=True,
        help="Directory containing *.timing.json files"
    )
    args = parser.parse_args()

    timing_files = sorted(
        glob.glob(os.path.join(args.timing_dir, "*.timing.json"))
    )

    if not timing_files:
        print(f"Warning: no *.timing.json files found in {args.timing_dir}",
              file=sys.stderr)
        return

    hostname = socket.gethostname()
    plat = f"{platform.system().lower()}-{platform.machine()}"
    sst_version = get_sst_version()
    jenkins_meta = get_jenkins_metadata()

    for tf in timing_files:
        record = build_record(tf, hostname, plat, sst_version, jenkins_meta)
        if record is None:
            continue
        sys.stdout.write(f"PARSER_BENCH_RESULT:{json.dumps(record)}\n")
        sys.stdout.flush()


if __name__ == '__main__':
    main()
