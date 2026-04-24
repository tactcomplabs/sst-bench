#!/usr/bin/env bash
#
# Copyright (C) 2017-2026 Tactical Computing Laboratories, LLC
# All Rights Reserved
# contact@tactcomplabs.com
#
# See LICENSE in the top level directory for licensing details
#
# ci-run-ctest.sh — Jenkins entrypoint replacing bare `ctest`.
#
# Runs the sanity ctest quietly, then a perf-tier ctest verbosely so
# ###SST_BENCH_PERF_V1### markers reach the Jenkins build log and get
# ingested by Logstash.
#
# Env:
#   SSTBENCH_PERF_TIER  fast|medium|heavy  (default: fast)
#
# Invoke from the CMake build directory (where CTestTestfile.cmake lives).
set -euo pipefail

TIER="${SSTBENCH_PERF_TIER:-fast}"

echo "=== sanity ctest (label: all) ==="
ctest --output-on-failure -L all

echo "=== perf ctest (label: perf-${TIER}) ==="
ctest -V --test-output-size-passed 0 -L "perf-${TIER}"
