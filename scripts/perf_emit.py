#!/usr/bin/env python3

#
# Copyright (C) 2017-2026 Tactical Computing Laboratories, LLC
# All Rights Reserved
# contact@tactcomplabs.com
#
# See LICENSE in the top level directory for licensing details
#
# perf_emit.py
#

import argparse
import datetime
import hashlib
import json
import os
import re
import socket
import subprocess
import sys
import uuid

SCHEMA_VERSION = 1
SENTINEL_START = "###SST_BENCH_PERF_V1###"
SENTINEL_END = "###END###"

# timing.simulated_time_ua -> nanoseconds. Supports "s","ms","us","ns","ps","fs".
_UNIT_TO_NS = {
    "s": 1_000_000_000.0,
    "ms": 1_000_000.0,
    "us": 1_000.0,
    "ns": 1.0,
    "ps": 1e-3,
    "fs": 1e-6,
}
_UA_RE = re.compile(r"^\s*([0-9.+-eE]+)\s*([a-zA-Z]+)\s*$")


def _parse_simulated_time_ns(ua):
    """Parse '1 ms' style algebra-seconds string to float ns. Returns None on fail."""
    if not isinstance(ua, str):
        return None
    m = _UA_RE.match(ua)
    if not m:
        return None
    try:
        value = float(m.group(1))
    except ValueError:
        return None
    unit = m.group(2).lower()
    mult = _UNIT_TO_NS.get(unit)
    if mult is None:
        return None
    return value * mult


def _benchmark_id(sweep_name, sdl_file, jobtype):
    """Stable identity excluding ranks/threads/param values — those are filter dims."""
    h = hashlib.sha1()
    h.update((sweep_name or "").encode("utf-8"))
    h.update(b"\x00")
    h.update(os.path.basename(sdl_file or "").encode("utf-8"))
    h.update(b"\x00")
    h.update((jobtype or "").encode("utf-8"))
    return h.hexdigest()[:16]


def _sst_version_or_none():
    try:
        out = subprocess.check_output(
            ["sst", "--version"], stderr=subprocess.DEVNULL, timeout=5
        ).decode("utf-8", errors="replace")
        m = re.search(r"\(([^)]+)\)", out)
        if m:
            return m.group(1).strip()
    except (subprocess.SubprocessError, FileNotFoundError, OSError):
        pass
    return None


def _sst_bench_sha_or_none():
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        out = subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=script_dir,
            stderr=subprocess.DEVNULL,
            timeout=5,
        ).decode("utf-8", errors="replace").strip()
        return out[:12] if out else None
    except (subprocess.SubprocessError, FileNotFoundError, OSError):
        pass
    return None


def _sdl_rel_path(sdl_file):
    """Repo-relative sdl path when SST_BENCH_HOME is set; else basename."""
    if not sdl_file:
        return None
    bench_home = os.environ.get("SST_BENCH_HOME")
    abs_sdl = os.path.abspath(sdl_file)
    if bench_home:
        try:
            rel = os.path.relpath(abs_sdl, os.path.abspath(bench_home))
            if not rel.startswith(".."):
                return rel
        except ValueError:
            pass
    return os.path.basename(abs_sdl)


def build_perf_record(timing_json_path, context):
    """Pure function: read timing.json + context dict -> perf record dict.

    context keys:
      run_id       str    required
      sweep_name   str    required
      sdl_file     str    path to sdl; required
      jobtype      str    "BASE"|"CPT"|"RST"; required
      jobid        int    required
      ranks        int    required
      threads      int    required
      nodes        int    optional, default 1
      sst_params   dict   optional
      sdl_params   dict   optional
      sst_version  str    optional; auto-detected if missing
      sst_bench_sha str   optional; auto-detected if missing
      host         str    optional; auto-detected if missing
    """
    with open(timing_json_path, "r") as f:
        timing_doc = json.load(f)
    timing = timing_doc.get("timing-info", timing_doc)

    sweep_name = context.get("sweep_name") or ""
    sdl_file = context.get("sdl_file") or ""
    jobtype = context.get("jobtype") or ""

    record = {
        "schema_version": SCHEMA_VERSION,
        "emitted_at": datetime.datetime.now(datetime.timezone.utc)
        .isoformat(timespec="seconds")
        .replace("+00:00", "Z"),
        "run_id": context["run_id"],
        "benchmark_id": _benchmark_id(sweep_name, sdl_file, jobtype),
        "sweep_name": sweep_name,
        "sdl_file": _sdl_rel_path(sdl_file),
        "jobtype": jobtype,
        "jobid": int(context["jobid"]),
        "ranks": int(context["ranks"]),
        "threads": int(context["threads"]),
        "nodes": int(context.get("nodes", 1)),
        "sst_version": context.get("sst_version") or _sst_version_or_none(),
        "sst_bench_sha": context.get("sst_bench_sha") or _sst_bench_sha_or_none(),
        "host": context.get("host") or socket.gethostname(),
        "sdl_params": context.get("sdl_params") or {},
        "sst_params": context.get("sst_params") or {},
        "timing": timing,
    }

    sim_ns = _parse_simulated_time_ns(timing.get("simulated_time_ua"))
    if sim_ns is not None:
        record["simulated_time_ns"] = sim_ns

    return record


def format_marker_line(record):
    payload = json.dumps(record, sort_keys=True, separators=(",", ":"), default=str)
    return f"{SENTINEL_START}{payload}{SENTINEL_END}"


def emit(record, stream=None):
    """Write the marker line + newline to stream (default stdout) and flush."""
    stream = stream or sys.stdout
    stream.write(format_marker_line(record))
    stream.write("\n")
    stream.flush()


def new_run_id():
    return str(uuid.uuid4())


def _load_context_arg(raw):
    if raw is None:
        return {}
    if raw.startswith("@"):
        with open(raw[1:], "r") as f:
            return json.load(f)
    return json.loads(raw)


def main(argv=None):
    ap = argparse.ArgumentParser(
        prog="perf_emit",
        description="Emit a SST-bench perf NDJSON marker line from a timing.json file",
    )
    ap.add_argument("--timing", required=True, help="path to timing.json")
    ap.add_argument(
        "--context-json",
        help='JSON context dict (or @path/to/ctx.json). Must include run_id, sweep_name, sdl_file, jobtype, jobid, ranks, threads.',
    )
    args = ap.parse_args(argv)

    ctx = _load_context_arg(args.context_json)
    missing = [k for k in ("run_id", "sweep_name", "sdl_file", "jobtype", "jobid", "ranks", "threads") if k not in ctx]
    if missing:
        print(f"perf_emit: missing required context keys: {missing}", file=sys.stderr)
        return 2

    record = build_perf_record(args.timing, ctx)
    emit(record)
    return 0


if __name__ == "__main__":
    sys.exit(main())
