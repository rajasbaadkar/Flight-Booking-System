from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.client import *
import os
import string
import random
from datetime import datetime
from prettytable import PrettyTable
import threading
os.system('color')
from termcolor import colored
import asyncio
import time
mutex = threading.Lock()
rate = 0.5
clock = 0 # Default rate 4 sec
queue = [] # Waitlist of clientId's requesting CS
queue_mutex = threading.Lock()
clientList = [] # List of clientIds
clientId = 0
client_mutex = threading.Lock()
critical_mutex = threading.Lock()
server = SimpleXMLRPCServer(('localhost', 4000), allow_none=True)
server_port = 4000
proxy1 = ServerProxy('http://localhost:3000')
proxy3 = ServerProxy('http://localhost:5000')
proxy4 = ServerProxy('http://localhost:6000')
proxy_list = [proxy1]
election_list = [proxy3, proxy4]
current_coordinator_port = 3000

def sendVictory(proxy):
    proxy.setCoordinator(server_port)

def setCoordinator(port):
    print('setCoordinator called for server 2...')
    global current_coordinator_port
    current_coordinator_port = port
    print('Set coordinator port as', port)

def doElection(): # set it up with clock
    '''
    1. Call the sendRequest of the election-list proxies to propogate the election
    2. Return "I am alive"
    '''
    flag = False
    pp = None
    for i, p in enumerate(election_list):
        try:
            init_time = time.time()
            print(f"Sending request to {[5000, 6000][i]}")
            # Send request and receive response from higher ID servers
            response = p.returnResponse()
            if int(time.time() - init_time) >= 5:
                flag = False
                break
            pp = p
            flag = True
            break
        except:
            continue
    if not flag:
        for i, p in enumerate(proxy_list):
            print(f"Sending victory msg to {[3000][i]}")
            sendVictory(p)
    else:
        flag = False
        print('Waiting...')
        t = threading.Thread(target=pp.doElection)
        t.start()
        # t.join()
        # pp.doElection()
    return

def returnResponse():
    print('Alive')
    return "Alive"

def set_interval(func, sec):
    def func_wrapper():
        set_interval(func, sec)
        func()
    t = threading.Timer(sec, func_wrapper)
    t.start()
    return t

def serverSynchronize():
    global clock
    mutex.acquire() # Keep increasing at "rate", keeping in mind race around condition
    clock += 1
    mutex.release()
    # print(colored(f"\n[INFO] Server Logical Clock(Updated at interval set): {clock}\n", 'yellow'))

def getServerClock(): # Server sends message to client
    return clock

def setServerClock(client_clock): # Server receives message from client
    global clock
    print(colored(f"\n[INFO] Before server recieves message: Server Logical Clock = {clock}\n", 'yellow'))
    if client_clock > clock:
        mutex.acquire()
        clock = client_clock + 1 # Send clock + 1 by default from client side
        mutex.release()
    print(colored(f"\n[INFO] After server recieves message: Server Logical Clock = {clock}\n", 'yellow'))

def requestCS(client_clock, clientID): # Server receives message from client
    global clock, critical_mutex, queue
    print(colored(f"\n[INFO] Before server recieves message: Server Logical Clock = {clock}\n", 'yellow'))
    if critical_mutex.locked():
        if clientID not in queue: # If not already in queue, add the client in queue
            queue_mutex.acquire()
            print(colored(f"Queue Mutex Acquired by {clientID}; queue:{queue}", "green"))
            queue.append(clientID) # Append to the queue
            queue
