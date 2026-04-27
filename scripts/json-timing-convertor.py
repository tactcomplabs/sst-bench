#!/usr/bin/env python3

#
# Copyright (C) 2017-2026 Tactical Computing Laboratories, LLC
# All Rights Reserved
# contact@tactcomplabs.com
#
# See LICENSE in the top level directory for licensing details
#
# json-timing-converter.py
#
# Converts SST16+ json timing data files to SST15 format

import json
import sys

UNITS={
    'B'     : 1,
    'KB'    : 1E3,
    'MB'    : 1E6,
    'GB'    : 1E9,
    'TB'    : 1E12,
}

def getFactor(unit):
    if unit not in UNITS.keys():
        print(f"error: {unit} not in [{UNITS}]")
        sys.exit(1)
    return UNITS[unit]

def toB(s):
    return round(float(s.split()[0]) * getFactor(s.split()[1]))

def toKB(s):
    return round(float(s.split()[0]) * getFactor(s.split()[1])/1E3)

def toMB(s):
    return round(float(s.split()[0]) * getFactor(s.split()[1])/1E6)

def assertSeconds(s):
    if s.split()[1] != "s":
        print(f"error: value not in seconds: {s}")
        sys.exit(1)
    return float(s.split()[0])

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: json-timing-convertor timing-file.json")
        exit(1)

    jsonFile = sys.argv[1]

    with open(jsonFile) as f:
        jsonDict = json.load(f)

    metadata=jsonDict['metadata']
    regions=jsonDict['regions']
    resources=jsonDict['resources']

    sst15Dict={ 
        'timing-info': {
            "local_max_rss":             toKB(resources['local_max_rss']),
            "global_max_rss":            toKB(resources['global_max_rss']),
            "local_max_pf":               int(resources['local_max_page_faults'].split()[0]),
            "global_pf":                  int(resources['global_page_faults']   .split()[0]),
            "global_max_io_in":           int(resources['global_max_io_in']     .split()[0]),
            "global_max_io_out":          int(resources['global_max_io_out']    .split()[0]),
            "global_max_sync_data_size":  toB(resources['global_max_sync_data_size']),
            "global_sync_data_size":      toB(resources['global_sync_data_size']),
            "max_mempool_size":           toB(resources['max_mempool_size']),
            "global_mempool_size":        toB(resources['global_mempool_size']),
            "global_active_activities":   int(resources['global_undeleted_activities']),
            "global_current_tv_depth":    int(resources['global_current_timevortex_depth'].split()[0]),
            "global_max_tv_depth":        int(resources['global_max_timevortex_depth'].split()[0]),
            "ranks":                       int(metadata['ranks']),
            "threads":                     int(metadata['threads']),
            "max_build_time":     assertSeconds(regions['total']['build']['duration']),
            "max_run_time":       assertSeconds(regions['total']['execute']['run']['duration']),
            "max_total_time":     assertSeconds(regions['total']['duration']),
            "simulated_time_ua":               metadata['simulation_time']
        }
    }

    print(json.dumps(sst15Dict, indent=2))

