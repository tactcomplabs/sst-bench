#!/usr/bin/env python3

#
# Copyright (C) 2017-2026 Tactical Computing Laboratories, LLC
# All Rights Reserved
#
# Unit tests for perf_emit.
#
# Run with:
#     python3 -m pytest scripts/tests/test_perf_emit.py
# or directly:
#     python3 scripts/tests/test_perf_emit.py
#

import io
import json
import os
import re
import sys
import tempfile
import unittest

SCRIPTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, SCRIPTS_DIR)

import perf_emit  # noqa: E402


TIMING_FIXTURE = {
    "timing-info": {
        "local_max_rss": 132256,
        "global_max_rss": 5055264,
        "local_max_pf": 669,
        "global_pf": 23423,
        "global_max_io_in": 6073,
        "global_max_io_out": 0,
        "global_max_sync_data_size": 48432,
        "global_sync_data_size": 1881250,
        "max_mempool_size": 11534336,
        "global_mempool_size": 461373440,
        "global_active_activities": 40,
        "global_current_tv_depth": 80,
        "global_max_tv_depth": 126,
        "max_build_time": 0.2318727970123291,
        "max_run_time": 6.7511022090911865,
        "max_total_time": 6.986878871917725,
        "simulated_time_ua": "1 ms",
    }
}


def _write_timing(fixture):
    fd, path = tempfile.mkstemp(suffix=".json")
    with os.fdopen(fd, "w") as f:
        json.dump(fixture, f)
    return path


def _base_ctx(**over):
    ctx = {
        "run_id": "11111111-2222-3333-4444-555555555555",
        "sweep_name": "grid_perf",
        "sdl_file": "benchmarks/grid/grid.py",
        "jobtype": "BASE",
        "jobid": 687804907541,
        "ranks": 4,
        "threads": 2,
        "nodes": 1,
        "sdl_params": {"clocks": 12, "size": 64},
        "sst_params": {"add-lib-path": "/opt/x"},
        "sst_version": "15.1.0",
        "sst_bench_sha": "abcdef123456",
        "host": "testhost",
    }
    ctx.update(over)
    return ctx


class TestBuildRecord(unittest.TestCase):

    def test_required_fields_and_schema_version(self):
        path = _write_timing(TIMING_FIXTURE)
        try:
            rec = perf_emit.build_perf_record(path, _base_ctx())
        finally:
            os.unlink(path)

        for key in ("schema_version", "emitted_at", "run_id", "benchmark_id",
                    "sweep_name", "sdl_file", "jobtype", "jobid", "ranks",
                    "threads", "nodes", "sst_version", "sst_bench_sha",
                    "host", "sdl_params", "sst_params", "timing"):
            self.assertIn(key, rec, f"missing {key}")
        self.assertEqual(rec["schema_version"], 1)
        self.assertEqual(rec["ranks"], 4)
        self.assertEqual(rec["threads"], 2)
        self.assertEqual(rec["timing"]["max_run_time"], 6.7511022090911865)

    def test_benchmark_id_stable_across_ranks(self):
        path = _write_timing(TIMING_FIXTURE)
        try:
            a = perf_emit.build_perf_record(path, _base_ctx(ranks=4, threads=2))
            b = perf_emit.build_perf_record(path, _base_ctx(ranks=64, threads=8))
            c = perf_emit.build_perf_record(path, _base_ctx(jobtype="CPT"))
        finally:
            os.unlink(path)
        # ranks/threads differ -> same benchmark_id (those are filter dimensions)
        self.assertEqual(a["benchmark_id"], b["benchmark_id"])
        # jobtype differs -> different benchmark_id (BASE vs CPT are separate series)
        self.assertNotEqual(a["benchmark_id"], c["benchmark_id"])

    def test_simulated_time_ns_parsed(self):
        path = _write_timing(TIMING_FIXTURE)
        try:
            rec = perf_emit.build_perf_record(path, _base_ctx())
        finally:
            os.unlink(path)
        self.assertAlmostEqual(rec["simulated_time_ns"], 1_000_000.0)

    def test_simulated_time_ns_missing_when_unparseable(self):
        fixture = {"timing-info": dict(TIMING_FIXTURE["timing-info"])}
        fixture["timing-info"]["simulated_time_ua"] = "forever"
        path = _write_timing(fixture)
        try:
            rec = perf_emit.build_perf_record(path, _base_ctx())
        finally:
            os.unlink(path)
        self.assertNotIn("simulated_time_ns", rec)

    def test_simulated_time_ns_unit_variants(self):
        cases = [
            ("1 s", 1_000_000_000.0),
            ("1 ms", 1_000_000.0),
            ("1 us", 1_000.0),
            ("1 ns", 1.0),
            ("1.5 ms", 1_500_000.0),
            ("2e3 us", 2_000_000.0),
        ]
        for ua, expected in cases:
            with self.subTest(ua=ua):
                self.assertAlmostEqual(perf_emit._parse_simulated_time_ns(ua), expected)


class TestEmitFormat(unittest.TestCase):

    def test_marker_roundtrip(self):
        path = _write_timing(TIMING_FIXTURE)
        try:
            rec = perf_emit.build_perf_record(path, _base_ctx())
        finally:
            os.unlink(path)

        buf = io.StringIO()
        perf_emit.emit(rec, stream=buf)
        line = buf.getvalue().rstrip("\n")

        self.assertTrue(line.startswith(perf_emit.SENTINEL_START))
        self.assertTrue(line.endswith(perf_emit.SENTINEL_END))
        # Exactly one marker per line
        self.assertEqual(line.count(perf_emit.SENTINEL_START), 1)
        self.assertEqual(line.count(perf_emit.SENTINEL_END), 1)
        # No embedded newlines in the payload
        self.assertNotIn("\n", line)

        m = re.match(
            re.escape(perf_emit.SENTINEL_START)
            + r"(.+?)"
            + re.escape(perf_emit.SENTINEL_END)
            + r"$",
            line,
        )
        self.assertIsNotNone(m)
        parsed = json.loads(m.group(1))
        self.assertEqual(parsed["schema_version"], 1)
        self.assertEqual(parsed["ranks"], 4)
        self.assertEqual(parsed["benchmark_id"], rec["benchmark_id"])

    def test_emit_appends_newline_and_flushes(self):
        path = _write_timing(TIMING_FIXTURE)
        try:
            rec = perf_emit.build_perf_record(path, _base_ctx())
        finally:
            os.unlink(path)
        buf = io.StringIO()
        perf_emit.emit(rec, stream=buf)
        self.assertTrue(buf.getvalue().endswith("\n"))


class TestCli(unittest.TestCase):

    def test_cli_main(self):
        path = _write_timing(TIMING_FIXTURE)
        ctx_fd, ctx_path = tempfile.mkstemp(suffix=".json")
        with os.fdopen(ctx_fd, "w") as f:
            json.dump(_base_ctx(), f)
        try:
            saved_stdout = sys.stdout
            sys.stdout = io.StringIO()
            try:
                rc = perf_emit.main(["--timing", path, "--context-json", f"@{ctx_path}"])
                out = sys.stdout.getvalue()
            finally:
                sys.stdout = saved_stdout
        finally:
            os.unlink(path)
            os.unlink(ctx_path)
        self.assertEqual(rc, 0)
        self.assertIn(perf_emit.SENTINEL_START, out)
        self.assertIn(perf_emit.SENTINEL_END, out)

    def test_cli_missing_keys(self):
        path = _write_timing(TIMING_FIXTURE)
        try:
            saved_err = sys.stderr
            sys.stderr = io.StringIO()
            try:
                rc = perf_emit.main(["--timing", path, "--context-json", "{}"])
                err = sys.stderr.getvalue()
            finally:
                sys.stderr = saved_err
        finally:
            os.unlink(path)
        self.assertEqual(rc, 2)
        self.assertIn("missing required context", err)


if __name__ == "__main__":
    unittest.main()
