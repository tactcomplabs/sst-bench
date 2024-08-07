#!/usr/bin/python3
#
# Copyright (C) 2017-2024 Tactical Computing Laboratories, LLC
# All Rights Reserved
# contact@tactcomplabs.com
#
# See LICENSE in the top level directory for licensing details
#
# run-test1.py

import socket
import os

BUFFER_SIZE = 1024

HOST = "127.0.0.1"
DEBUG_PORT = int(os.getenv("DEBUG_PORT", 0))

if DEBUG_PORT == 0:
    print("Debug port set to 0. Nothing to do")
    exit(0)

count = 0
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, DEBUG_PORT))
    msg=f"Count={count}".encode('utf-8')
    s.sendall(msg)
    data = s.recv(BUFFER_SIZE)
    count = count + 1

print(f"Received {data!r}")


