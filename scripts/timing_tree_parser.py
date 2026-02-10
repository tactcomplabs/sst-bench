#!/usr/bin/env python3

#
# Copyright (C) 2017-2025 Tactical Computing Laboratories, LLC
# All Rights Reserved
# contact@tactcomplabs.com
#
# See LICENSE in the top level directory for licensing details
#
# timing_tree_parser.py
#
# Parser for SST --print-timing-info=N text output
#

"""
Parse SST's --print-timing-info text output into a nested dictionary structure.

Input format (from sst -v --print-timing-info=10 ...):

Simulation Resource Utilization for Code Regions:
■ total
│ ├── Duration: 1473.583 seconds
│ └── Memory: Total - 1.301 GB
├ ■ build
│ │ ├── Duration: 947.986 seconds
│ │ └── Memory: Total - 184.7 MB
│ ├ ■ graph-processing
│ │ │ ├── Duration: 947.681 seconds
...

Output structure:
{
    "total": {
        "duration_sec": 1473.583,
        "memory_gb": 1.301,
        "children": {
            "build": {
                "duration_sec": 947.986,
                "memory_mb": 184.7,
                "children": {...}
            }
        }
    }
}
"""

import re
import sys
from typing import Optional


def parse_timing_output(text: str) -> dict:
    """
    Parse SST --print-timing-info text output into a nested dictionary.

    Args:
        text: Raw text output from SST with timing information

    Returns:
        Nested dictionary with timing tree structure
    """
    lines = text.strip().split('\n')

    # Find the start of timing output
    start_idx = None
    for i, line in enumerate(lines):
        if 'Simulation Resource Utilization' in line:
            start_idx = i + 1
            break

    if start_idx is None:
        return {}

    # Parse the tree structure
    root = {}
    node_stack = [(root, -1)]  # (node, depth)

    # Patterns for parsing
    # Node name pattern: looks for ■ followed by node name
    node_pattern = re.compile(r'^([│├└ ]*)[■][ ]+(\S+)')
    # Duration pattern
    duration_pattern = re.compile(r'Duration:\s*([\d.]+)\s*(\w+)')
    # Memory pattern
    memory_pattern = re.compile(r'Memory:\s*Total\s*-\s*([\d.]+)\s*(\w+)')

    current_node = None
    current_depth = 0

    for line in lines[start_idx:]:
        # Skip empty lines
        if not line.strip():
            continue

        # Check for node name
        node_match = node_pattern.match(line)
        if node_match:
            prefix = node_match.group(1)
            name = node_match.group(2)

            # Calculate depth based on prefix characters
            # Count structural characters (├, │, └) and spaces
            depth = 0
            for char in prefix:
                if char in '├│└':
                    depth += 1

            # Create new node
            new_node = {
                'duration_sec': 0.0,
                'children': {}
            }

            # Find parent based on depth
            while len(node_stack) > 1 and node_stack[-1][1] >= depth:
                node_stack.pop()

            # Add to parent's children
            parent = node_stack[-1][0]
            if 'children' not in parent:
                parent['children'] = {}
            parent['children'][name] = new_node

            # Push to stack
            node_stack.append((new_node, depth))
            current_node = new_node
            continue

        # Check for duration
        duration_match = duration_pattern.search(line)
        if duration_match and current_node is not None:
            value = float(duration_match.group(1))
            unit = duration_match.group(2).lower()
            # Convert to seconds
            if unit == 'seconds' or unit == 'sec' or unit == 's':
                current_node['duration_sec'] = value
            elif unit == 'milliseconds' or unit == 'ms':
                current_node['duration_sec'] = value / 1000.0
            elif unit == 'minutes' or unit == 'min':
                current_node['duration_sec'] = value * 60.0
            else:
                current_node['duration_sec'] = value
            continue

        # Check for memory
        memory_match = memory_pattern.search(line)
        if memory_match and current_node is not None:
            value = float(memory_match.group(1))
            unit = memory_match.group(2).upper()
            if unit == 'GB':
                current_node['memory_gb'] = value
            elif unit == 'MB':
                current_node['memory_mb'] = value
            elif unit == 'KB':
                current_node['memory_kb'] = value
            elif unit == 'B':
                current_node['memory_b'] = value
            continue

    # Return the children of root (top-level nodes like 'total')
    return root.get('children', {})


def get_metric(tree: dict, path: str) -> Optional[float]:
    """
    Extract a metric by path from the timing tree.

    Args:
        tree: Parsed timing tree dictionary
        path: Slash-separated path to metric (e.g., "total/build/graph-processing")
              Optionally append metric name after colon (e.g., "total:duration_sec")

    Returns:
        The metric value, or None if not found
    """
    parts = path.split('/')
    metric_name = 'duration_sec'  # default

    # Check if last part specifies the metric
    if ':' in parts[-1]:
        parts[-1], metric_name = parts[-1].rsplit(':', 1)

    current = tree
    for part in parts:
        if part in current:
            current = current[part]
        elif 'children' in current and part in current['children']:
            current = current['children'][part]
        else:
            return None

    # Return the requested metric
    if isinstance(current, dict):
        return current.get(metric_name)
    return None


def flatten_metrics(tree: dict, prefix: str = '') -> dict:
    """
    Flatten the timing tree into a single-level dictionary for Logstash output.

    Args:
        tree: Parsed timing tree dictionary
        prefix: Prefix for keys (used in recursion)

    Returns:
        Flattened dictionary with keys like "total_duration_sec", "build_duration_sec"
    """
    result = {}

    for name, node in tree.items():
        key_prefix = f"{prefix}{name}_" if prefix else f"{name}_"

        # Add metrics for this node
        if 'duration_sec' in node:
            result[f"{key_prefix}duration_sec"] = node['duration_sec']
        if 'memory_gb' in node:
            result[f"{key_prefix}memory_gb"] = node['memory_gb']
        if 'memory_mb' in node:
            result[f"{key_prefix}memory_mb"] = node['memory_mb']
        if 'memory_kb' in node:
            result[f"{key_prefix}memory_kb"] = node['memory_kb']

        # Recurse into children
        if 'children' in node and node['children']:
            child_metrics = flatten_metrics(node['children'], key_prefix)
            result.update(child_metrics)

    return result


def extract_key_metrics(tree: dict) -> dict:
    """
    Extract the key metrics needed for the benchmark output.

    Args:
        tree: Parsed timing tree dictionary

    Returns:
        Dictionary with standardized metric names for Logstash output
    """
    metrics = {}

    # Total metrics
    total = tree.get('total', {})
    metrics['total_duration_sec'] = total.get('duration_sec', 0.0)
    if 'memory_gb' in total:
        metrics['total_memory_gb'] = total['memory_gb']
    elif 'memory_mb' in total:
        metrics['total_memory_gb'] = total['memory_mb'] / 1024.0

    # Build metrics
    build = total.get('children', {}).get('build', {})
    metrics['build_duration_sec'] = build.get('duration_sec', 0.0)
    if 'memory_mb' in build:
        metrics['build_memory_mb'] = build['memory_mb']
    elif 'memory_gb' in build:
        metrics['build_memory_mb'] = build['memory_gb'] * 1024.0

    # Graph processing metrics
    graph_proc = build.get('children', {}).get('graph-processing', {})
    metrics['graph_processing_duration_sec'] = graph_proc.get('duration_sec', 0.0)

    # Model generation metrics
    model_gen = graph_proc.get('children', {}).get('model-generation', {})
    metrics['model_generation_duration_sec'] = model_gen.get('duration_sec', 0.0)

    # Model execution metrics (this is the key parsing metric)
    model_exec = model_gen.get('children', {}).get('model-execution', {})
    metrics['model_execution_duration_sec'] = model_exec.get('duration_sec', 0.0)

    # Execute/run metrics
    execute = total.get('children', {}).get('execute', {})
    metrics['execute_duration_sec'] = execute.get('duration_sec', 0.0)

    run = execute.get('children', {}).get('run', {})
    metrics['run_duration_sec'] = run.get('duration_sec', 0.0)

    return metrics


if __name__ == '__main__':
    import argparse
    import json

    parser = argparse.ArgumentParser(
        prog="timing_tree_parser.py",
        description="Parse SST --print-timing-info text output into structured data")
    parser.add_argument("--input", "-i", type=str,
                        help="Input file (reads from stdin if not specified)")
    parser.add_argument("--output", "-o", type=str,
                        help="Output JSON file (writes to stdout if not specified)")
    parser.add_argument("--flatten", "-f", action="store_true",
                        help="Flatten output for Logstash compatibility")
    parser.add_argument("--key-metrics", "-k", action="store_true",
                        help="Extract only key benchmark metrics")
    parser.add_argument("--get", "-g", type=str,
                        help="Get specific metric by path (e.g., 'total/build:duration_sec')")

    args = parser.parse_args()

    # Read input
    if args.input:
        with open(args.input, 'r') as f:
            text = f.read()
    else:
        text = sys.stdin.read()

    # Parse timing output
    tree = parse_timing_output(text)

    # Generate output based on options
    if args.get:
        value = get_metric(tree, args.get)
        if value is not None:
            print(value)
        else:
            print(f"Metric not found: {args.get}", file=sys.stderr)
            sys.exit(1)
    elif args.key_metrics:
        result = extract_key_metrics(tree)
        output = json.dumps(result, indent=2)
        if args.output:
            with open(args.output, 'w') as f:
                f.write(output)
        else:
            print(output)
    elif args.flatten:
        result = flatten_metrics(tree)
        output = json.dumps(result, indent=2)
        if args.output:
            with open(args.output, 'w') as f:
                f.write(output)
        else:
            print(output)
    else:
        output = json.dumps(tree, indent=2)
        if args.output:
            with open(args.output, 'w') as f:
                f.write(output)
        else:
            print(output)
