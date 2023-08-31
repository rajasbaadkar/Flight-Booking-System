import concurrent.futures
import time
import asyncio
from termcolor import colored
from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.client import *
import os
import string
import random
from datetime import datetime
from prettytable import PrettyTable
import threading
os.system('color')
os.system('color')

# Load balance among the list of servers
server_list = [3000, 4000]#, 5000, 6000]
i = -1  # Current server index
mutex = threading.Lock()
rate = 0.5
clock = 0
server = SimpleXMLRPCServer(('localhost', 3500), allow_none=True)
server_port = 3500


def get_server():
    global i
    i = (i+1) % len(server_list)
    return server_list[i]


def set_interval(func, sec):
    def func_wrapper():
        set_interval(func, sec)
        func()
    t = threading.Timer(sec, func_wrapper)
    t.start()
    return t


def serverSynchronize():
    global clock
    mutex.acquire()  # Keep increasing at "rate", keeping in mind race around condition
    clock += 1
    mutex.release()
    # print(colored(f"\n[INFO] Server Logical Clock(Updated at interval set): {clock}\n", 'yellow'))

# Lamport's Algorithm


def getServerClock():  # Server sends message to client
    return clock


def setServerClock(client_clock):  # Server receives message from client
    global clock
    print(colored(
        f"\n[INFO] Before server recieves message: Server Logical Clock = {clock}\n", 'yellow'))
    if client_clock > clock:
        mutex.acquire()
        clock = client_clock + 1  # Send clock + 1 by default from client side
        mutex.release()
    print(colored(
        f"\n[INFO] After server recieves message: Server Logical Clock = {clock}\n", 'yellow'))


server.register_function(get_server)
server.register_function(setServerClock)
server.register_function(getServerClock)

if __name__ == '__main__':
    print('Load Balancer Serving...')
    set_interval(serverSynchronize, rate)
    server.serve_forever()
