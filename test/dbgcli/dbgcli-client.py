#!/usr/bin/python3
#
# Copyright (C) 2017-2024 Tactical Computing Laboratories, LLC
# All Rights Reserved
# contact@tactcomplabs.com
#
# See LICENSE in the top level directory for licensing details
#
# run-client.py

import os
import socket
import sys

from enum import Enum

BUFFER_SIZE = 1024
HOST = "127.0.0.1"
PROBE_PORT = int(os.getenv("PROBE_PORT", 0))

class State(Enum):
    INIT = 0
    RUN = 1
    DISCONNECT = 2

def decode(msg):
    global state
    cmd = msg.lower().strip()
    if cmd=="disconnect" or cmd=="quit" or cmd=="exit" or cmd=="bye":
        state = State.DISCONNECT

def client_program():
    global state
    client_socket = socket.socket()
    print(f"Connecting to {HOST}:{PROBE_PORT}")
    client_socket.connect( (HOST, PROBE_PORT) )

    # provite socket server identification
    state = State.INIT
    divider = "##################################"
    print(divider)

    cmd = "hostname"
    client_socket.send(cmd.encode())
    servername = client_socket.recv(BUFFER_SIZE).decode()
    print(f"# {cmd} = {servername}")

    cmd = "component"
    client_socket.send(cmd.encode())
    comp = client_socket.recv(BUFFER_SIZE).decode()
    print(f"# {cmd} = {comp}")

    cmd = "cycle"
    client_socket.send(cmd.encode())
    cycle = client_socket.recv(BUFFER_SIZE).decode()
    print(f"# {cmd} = {cycle}")

    print(divider)

    state = State.RUN
    while state == State.RUN:
        client_socket.send("cycle".encode())
        cycle = client_socket.recv(BUFFER_SIZE).decode()
        PROMPT = f"[probe:{comp}:{cycle}]> "
        msg = input(PROMPT)
        decode(msg)
        if state == State.DISCONNECT:
            msg = "disconnect"
        client_socket.send(msg.encode())
        data = client_socket.recv(BUFFER_SIZE).decode()
        print(data)

    client_socket.close()

if __name__ == '__main__':
    try:
        client_program()
    except Exception as err:
        print(f"disconnected: {err=}, {type(err)=}")
    else:
        print("dbgcli-client completed normally")
        





