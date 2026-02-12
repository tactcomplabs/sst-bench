#!/usr/bin/env python3

#
# Copyright (C) 2017-2025 Tactical Computing Laboratories, LLC
# All Rights Reserved
# contact@tactcomplabs.com
#
# See LICENSE in the top level directory for licensing details
#
# parser-bench-sweep.py
#
# Parameter sweep driver for parser benchmarking with SQLite output.
# Generates configs via config_generator, runs SST, and stores timing
# data in SQLite using sqlutils (same backend as sst-perfdb/sst-sweeper).
#
# Sweep dimensions: component count x topology x config format
# Single-rank only — rank/thread sweeping is the sweeper's domain.
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

# Add scripts directory to path for local imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import jobutils
import sqlutils
from config_generator import generate_config
from timing_tree_parser import parse_timing_output, extract_key_metrics

g_pfx = "[parser-bench-sweep]"


def get_sst_version():
    """Get SST version string."""
    try:
        result = subprocess.run(['sst', '--version'], capture_output=True, text=True)
        match = re.search(r'(\d+\.\d+\.\d+)', result.stdout + result.stderr)
        return match.group(1) if match else "unknown"
    except Exception:
        return "unknown"


def parse_csv_ints(value):
    """Parse comma-separated integers."""
    return [int(x.strip()) for x in value.split(',')]


def parse_csv_strings(value):
    """Parse comma-separated strings."""
    return [x.strip() for x in value.split(',')]


class SweepManager:
    """Manages the parameter sweep: config generation, SST execution, SQLite storage."""

    def __init__(self, args):
        self.args = args
        self.jutil = jobutils.JobUtil("sweep")

        # Find unique run directory: {tmpdir}/{jobname}[.N]
        tdir = os.path.abspath(args.tmpdir)
        os.makedirs(tdir, exist_ok=True)
        rdir = os.path.join(tdir, args.jobname)
        self.rundir = rdir
        i = 0
        while os.path.isdir(self.rundir):
            i += 1
            if i >= 10000:
                print(f"{g_pfx} unable to find unique run directory",
                      file=sys.stderr)
                sys.exit(1)
            self.rundir = f"{rdir}.{i}"
        os.makedirs(self.rundir)

        # SQLite database
        self.sqldb = sqlutils.sqldb(os.path.abspath(args.db), args.logging)

        # Job ID counter (same scheme as sst-perfdb)
        self._next_id = (int(datetime.timestamp(datetime.now()) * 10)
                         & 0xffffff) << 16

    def next_job_id(self):
        jid = self._next_id
        self._next_id += 1
        return jid

    def build_sst_cmd(self, config_file):
        """Build SST command parts for a sweep point."""
        parts = ['sst', '-v', '--print-timing-info=10',
                 '--timing-info-json=timing.json',
                 '--output-json=config.json']
        if self.args.add_lib_path:
            parts.append(f'--add-lib-path={self.args.add_lib_path}')
        parts.append(config_file)
        return parts

    def run_sst(self, cmd_parts, cwd):
        """Run SST, capture output, write log. Returns (rc, stdout, stderr)."""
        result = subprocess.run(cmd_parts, cwd=cwd,
                                capture_output=True, text=True)
        log_path = os.path.join(cwd, "log")
        with open(log_path, 'w') as f:
            f.write(result.stdout)
            if result.stderr:
                f.write(result.stderr)
        if result.returncode != 0:
            print(f"{g_pfx} error: {' '.join(cmd_parts)}: "
                  f"{(result.stderr or '')[:200]}", file=sys.stderr)
        return result.returncode, result.stdout, result.stderr

    def store_timing_info(self, jobid, jobpath):
        """Read timing.json and insert into timing_info table.

        Adds ranks=1, threads=1 since this script runs single-rank only.
        Uses insertRecord directly because the SST timing JSON does not
        include the ranks/threads fields that the table schema requires.
        """
        timing_file = os.path.join(jobpath, 'timing.json')
        try:
            with open(timing_file) as f:
                data = json.load(f)['timing-info']
            data['ranks'] = 1
            data['threads'] = 1
            self.sqldb.insertRecord(jobid, data, sqlutils.timingInfoTable)
        except (FileNotFoundError, KeyError, json.JSONDecodeError) as e:
            print(f"{g_pfx} warning: timing info for job {jobid}: {e}",
                  file=sys.stderr)

    def store_conf_info(self, jobid, jobpath):
        """Read SST --output-json and insert into conf_info table.

        Handles noodle component params by filling 0 for grid-specific
        fields (numBytes, minData, maxData, minDelay, maxDelay) that are
        not present in noodle configurations.
        """
        config_file = os.path.join(jobpath, 'config.json')
        try:
            with open(config_file) as f:
                cfg = json.load(f)

            po = cfg.get("program_options", {})
            components = cfg.get("components", [])
            links = cfg.get("links", [])
            stats = cfg.get("statistics_options", {})

            ci = {}
            ci["components"] = len(components)
            ci["links"] = len(links)
            ci["statisticOutput"] = stats.get("statisticOutput", "")
            ci["timebase"] = po.get("timebase", "")
            ci["partitioner"] = po.get("partitioner", "")
            ci["timeVortex"] = po.get("timeVortex", "")
            ci["checkpoint-sim-period"] = po.get("checkpoint-sim-period", "")
            ci["checkpoint-wall-period"] = po.get("checkpoint-wall-period", "")

            if components:
                c0 = components[0]
                ci["comp-name"] = c0.get("name", "")
                ci["comp-type"] = c0.get("type", "")
                p = c0.get("params", {})
                ci["numPorts"] = p.get("numPorts", 0)
                ci["clocks"] = p.get("clocks", 0)
                ci["rngSeed"] = p.get("rngSeed", 0)
                ci["clockFreq"] = p.get("clockFreq", "")
                # Grid-specific fields default to 0 for noodle configs
                ci["numBytes"] = p.get("numBytes", 0)
                ci["minData"] = p.get("minData", 0)
                ci["maxData"] = p.get("maxData", 0)
                ci["minDelay"] = p.get("minDelay", 0)
                ci["maxDelay"] = p.get("maxDelay", 0)
            else:
                for k in ["comp-name", "comp-type", "clockFreq"]:
                    ci[k] = ""
                for k in ["numBytes", "numPorts", "minData", "maxData",
                          "minDelay", "maxDelay", "clocks", "rngSeed"]:
                    ci[k] = 0

            self.sqldb.insertRecord(jobid, ci, sqlutils.confInfoTable)
        except (FileNotFoundError, KeyError, json.JSONDecodeError) as e:
            print(f"{g_pfx} warning: conf info for job {jobid}: {e}",
                  file=sys.stderr)

    def emit_ndjson(self, *, jobid, stdout_text, stderr_text,
                    num_comps, topology, config_format, run_num):
        """Parse timing tree from SST output and emit NDJSON line to stdout."""
        try:
            timing_text = (stderr_text or '') + (stdout_text or '')
            tree = parse_timing_output(timing_text)
            metrics = extract_key_metrics(tree)

            record = {
                "@timestamp": datetime.now(timezone.utc).isoformat(),
                "benchmark": "parser-bench",
                "hostname": socket.gethostname(),
                "platform": f"{platform.system().lower()}-{platform.machine()}",
                "sst_version": get_sst_version(),
                "jobid": jobid,
                "config_type": config_format,
                "topology": topology,
                "num_components": num_comps,
                "run_number": run_num,
            }
            record.update(metrics)
            print(json.dumps(record))
            sys.stdout.flush()
        except Exception as e:
            print(f"{g_pfx} warning: NDJSON for job {jobid}: {e}",
                  file=sys.stderr)

    def run_sweep_point(self, *, num_comps, topology, config_format,
                        run_num, params):
        """Generate config, run SST, store results for one sweep point."""
        jobid = self.next_job_id()
        jobpath = os.path.join(self.rundir, str(jobid))
        os.makedirs(jobpath, exist_ok=True)

        # Generate config file (baked-in params, no SDL overrides)
        ext = '.py' if config_format == 'python' else '.json'
        config_name = f"bench_{num_comps}_{topology}_{config_format}{ext}"
        config_path = os.path.join(jobpath, config_name)

        generate_config(
            num_comps=num_comps,
            ports_per_comp=self.args.ports_per_comp,
            topology=topology,
            output_format=config_format,
            output_path=config_path,
            params=params
        )

        # Build and display SST command
        cmd_parts = self.build_sst_cmd(config_name)
        cmd_str = ' '.join(cmd_parts)

        desc = f"{config_format}/{topology}/{num_comps}comps/run{run_num}"
        print(f"{g_pfx} job {jobid} {desc}: {cmd_str}")

        if self.args.norun:
            return

        # Execute SST
        rc, stdout_text, stderr_text = self.run_sst(cmd_parts, jobpath)
        if rc != 0:
            print(f"{g_pfx} warning: job {jobid} exited with code {rc}",
                  file=sys.stderr)

        # Store timing data in SQLite (from --timing-info-json)
        self.store_timing_info(jobid, jobpath)

        # Store config data in SQLite (from --output-json)
        self.store_conf_info(jobid, jobpath)

        # Store job info with sweep metadata encoded in jobtype
        job_data = {
            "friend": 0,
            "jobtype": f"PARSER_BENCH:{config_format}:{topology}:{num_comps}",
            "jobstring": cmd_str,
            "slurm": False,
            "cwd": jobpath,
            "cpt_num": 0,
            "cpt_timestamp": 0,
            "nodeclamp": 0,
            "jobnodes": 1,
        }
        self.sqldb.job_info(jobid=jobid, dataDict=job_data)
        self.sqldb.commit()

        # Optional NDJSON output (from --print-timing-info via timing_tree_parser)
        if self.args.ndjson:
            self.emit_ndjson(
                jobid=jobid,
                stdout_text=stdout_text,
                stderr_text=stderr_text,
                num_comps=num_comps,
                topology=topology,
                config_format=config_format,
                run_num=run_num
            )

    def launch(self, comp_range, topologies, formats, runs, params):
        """Run the full parameter sweep."""
        total = len(comp_range) * len(topologies) * len(formats) * runs
        print(f"{g_pfx} {total} jobs planned in {self.rundir}")
        print(f"{g_pfx} components: {comp_range}")
        print(f"{g_pfx} topologies: {topologies}")
        print(f"{g_pfx} formats:    {formats}")
        print(f"{g_pfx} runs/cfg:   {runs}")
        print(f"{g_pfx} database:   {os.path.abspath(self.args.db)}")

        if not self.args.noprompt:
            resp = input("continue? [Yn] ")
            if resp not in ("Y", "y", ""):
                print("exiting...")
                sys.exit(0)

        for num_comps in comp_range:
            for topology in topologies:
                for config_format in formats:
                    for run_num in range(1, runs + 1):
                        self.run_sweep_point(
                            num_comps=num_comps,
                            topology=topology,
                            config_format=config_format,
                            run_num=run_num,
                            params=params
                        )

        self.sqldb.close()
        print(f"{g_pfx} complete")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog="parser-bench-sweep.py",
        description="Parser benchmark parameter sweep with SQLite storage",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Quick test
  python3 scripts/parser-bench-sweep.py \\
      --comp-range 4,8 --runs 1 --noprompt

  # Full sweep
  python3 scripts/parser-bench-sweep.py \\
      --comp-range 4,8,16,50,100 \\
      --topologies chain,fully-connected \\
      --formats json,python \\
      --runs 3 --db parser-bench.db --noprompt

  # With NDJSON output
  python3 scripts/parser-bench-sweep.py \\
      --comp-range 100 --topologies chain --formats json \\
      --runs 1 --ndjson --noprompt

  # Dry run (print commands only)
  python3 scripts/parser-bench-sweep.py \\
      --comp-range 4,8,16 --norun --noprompt
""")

    parser.add_argument("--comp-range", type=str, required=True,
                        help="Comma-separated component counts "
                             "(e.g. 4,8,16,50,100)")
    parser.add_argument("--topologies", type=str,
                        default="chain,fully-connected",
                        help="Comma-separated topologies "
                             "[chain,fully-connected]")
    parser.add_argument("--formats", type=str, default="json,python",
                        help="Comma-separated config formats [json,python]")
    parser.add_argument("--runs", type=int, default=3,
                        help="Runs per configuration [3]")
    parser.add_argument("--db", type=str, default="parser-bench.db",
                        help="SQLite database file [parser-bench.db]")
    parser.add_argument("--clocks", type=int, default=1000,
                        help="Simulation clock cycles [1000]")
    parser.add_argument("--ports-per-comp", type=int, default=1,
                        help="Ports per component [1]")
    parser.add_argument("--rng-seed", type=int, default=31337,
                        help="Base RNG seed [31337]")
    parser.add_argument("--ndjson", action="store_true",
                        help="Also emit NDJSON to stdout")
    parser.add_argument("--jobname", type=str, default="parser-bench",
                        help="Job name prefix for run directory [parser-bench]")
    parser.add_argument("--tmpdir", type=str, default=".",
                        help="Working directory for runs [.]")
    parser.add_argument("--norun", action="store_true",
                        help="Print commands without executing")
    parser.add_argument("--noprompt", action="store_true",
                        help="Skip confirmation prompt")
    parser.add_argument("--add-lib-path", type=str, default="",
                        help="SST component library path for noodle")
    parser.add_argument("--logging", action="store_true",
                        help="Enable SQL logging")

    args = parser.parse_args()

    # Parse list arguments
    comp_range = parse_csv_ints(args.comp_range)
    topologies = parse_csv_strings(args.topologies)
    formats = parse_csv_strings(args.formats)

    # Validate topologies and formats
    for t in topologies:
        if t not in ('chain', 'fully-connected'):
            print(f"error: unknown topology '{t}'. "
                  f"Use: chain, fully-connected", file=sys.stderr)
            sys.exit(1)
    for f in formats:
        if f not in ('json', 'python'):
            print(f"error: unknown format '{f}'. "
                  f"Use: json, python", file=sys.stderr)
            sys.exit(1)

    # Component parameters for config_generator
    params = {
        'clock_freq': '1GHz',
        'clocks': args.clocks,
        'rng_seed': args.rng_seed,
        'msgs_per_clock': 1,
        'bytes_per_clock': 8,
        'ports_per_clock': 1,
        'link_latency': '1us',
        'verbose': 0,
    }

    mgr = SweepManager(args)
    mgr.launch(comp_range, topologies, formats, args.runs, params)
