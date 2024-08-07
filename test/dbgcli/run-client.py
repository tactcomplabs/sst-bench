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

BUFFER_SIZE = 1024
HOST = "127.0.0.1"
DEBUG_PORT = int(os.getenv("DEBUG_PORT", 0))
PROMPT = "sstdbg -> "

def isAlive(msg):
    cmd = msg.lower().strip();
    if cmd == "quit":
        return False
    if cmd == "exit":
        return False
    return True

def client_program():
    client_socket = socket.socket()
    client_socket.connect( (HOST, DEBUG_PORT) )
    msg = input(PROMPT)
    while isAlive(msg):
        client_socket.send(msg.encode()) 
        data = client_socket.recv(BUFFER_SIZE).decode()
        print(data)
        msg = input(PROMPT)
    client_socket.close()

if __name__ == '__main__':
    client_program()




