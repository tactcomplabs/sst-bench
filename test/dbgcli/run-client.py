#!/usr/bin/python3
#
# Copyright (C) 2017-2024 Tactical Computing Laboratories, LLC
# All Rights Reserved
# contact@tactcomplabs.com
#
# See LICENSE in the top level directory for licensing details
#
# run-client.py

import socket
import os
from enum import Enum

BUFFER_SIZE = 1024
HOST = "127.0.0.1"
PROBE_PORT = int(os.getenv("PROBE_PORT", 0))
PROMPT = "sstdbg -> "

class State(Enum):
    RUN = 0
    DISCONNECT = 1

state = State.RUN

def decode(msg):
    global state
    cmd = msg.lower().strip()
    if cmd=="disconnect" or cmd=="quit" or cmd=="exit" or cmd=="bye":
        state = State.DISCONNECT

def client_program():
    global state
    client_socket = socket.socket()
    client_socket.connect( (HOST, PROBE_PORT) )
    while state == State.RUN:
        msg = input(PROMPT)
        decode(msg)
        if state == State.DISCONNECT:
            msg = "disconnect"
        client_socket.send(msg.encode())
        data = client_socket.recv(BUFFER_SIZE).decode()
        print(data)

    client_socket.close()

if __name__ == '__main__':
    client_program()




