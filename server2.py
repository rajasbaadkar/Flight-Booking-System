import pandas as pd
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

mutex = threading.Lock()
rate = 0.5
clock = 0  # Default rate 4 sec
queue = []  # Waitlist of clientId's requesting CS
queue_mutex = threading.Lock()
clientList = []  # List of clientIds
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
df = None


def sendVictory(proxy):
    proxy.setCoordinator(server_port)


def setCoordinator(port):
    # print('setCoordinator called for server 2...')
    global current_coordinator_port
    current_coordinator_port = port
    # print('Set coordinator port as',port)


def doElection():  # set it up with clock
    '''
    1. Call the sendRequest of the election-list proxies to propogate the election
    2. Return "I am alive"
    '''
    flag = False
    pp = None
    for i, p in enumerate(election_list):
        try:
            init_time = time.time()
            # print(f"Sending request to {[5000, 6000][i]}")
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
            # print(f"Sending victory msg to {[3000][i]}")
            sendVictory(p)
    else:
        flag = False
        # print('Waiting...')
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

# Mutual Exclusion using Centralized Algorithm


def requestCS(client_clock, clientID):  # Server receives message from client
    global clock, critical_mutex, queue
    print(colored(
        f"\n[INFO] Before server recieves message: Server Logical Clock = {clock}\n", 'yellow'))
    if critical_mutex.locked():
        if clientID not in queue:  # If not already in queue, add the client in queue
            queue_mutex.acquire()
            print(
                colored(f"Queue Mutex Acquired by {clientID}; queue:{queue}", "green"))
            queue.append(clientID)  # Append to the queue
            queue_mutex.release()
            print(
                colored(f"Queue released by {clientID}; queue:{queue}", "green"))
        return False
    else:
        critical_mutex.acquire()
        print(colored(f"\nCritical Mutex Acquired by {clientID}", "red"))
        if client_clock > clock:
            mutex.acquire()
            clock = client_clock + 1  # Send clock + 1 by default from client side
            mutex.release()
        print(colored(
            f"\n[INFO] After server recieves message: Server Logical Clock = {clock}\n", 'yellow'))
        if clientID in queue:
            print(
                colored(f"Queue Mutex Acquired by {clientID}; queue:{queue}", "green"))
            queue_mutex.acquire()
            try:
                queue.remove(clientID)  # Remove
            except:
                pass
            queue_mutex.release()
            print(
                colored(f"Queue released by {clientID}; queue:{queue}", "green"))
        return True


def releaseCS(client_clock, clientID):  # Server receives message from client
    global clock, critical_mutex
    print(colored(
        f"\n[INFO] Before server recieves message: Server Logical Clock = {clock}\n", 'yellow'))
    if client_clock > clock:
        mutex.acquire()
        clock = client_clock + 1  # Send clock + 1 by default from client side
        mutex.release()
    print(colored(
        f"\n[INFO] After server recieves message: Server Logical Clock = {clock}\n", 'yellow'))
    critical_mutex.release()
    print(colored(f"\nCritical Mutex Released by {clientID}", "red"))
    return clock

# Model classes


class User():
    def __init__(self, username):
        self.username = username  # User Identification information
        self.history = []  # Contain the list of flights, along with booked status
        self.curr_flight = None  # Contains the active flights if any

    def __str__(self):
        return f"['username': {self.username}, 'history': {self.history}, 'curr_flight': {self.curr_flight}]"

    def addToSeen(self, f):
        self.history.append(
            {"flight": f['flight_number'].values[0], "status": "seen"})
        print('inside addToSeen')
        self.curr_flight = f

    def bookFlight(self, flight_class, id):
        global df
        # ACQUIRE DB ACCESS HERE
        with open('db_lock.txt', 'r+') as f:
            while (f.read() == "1"):
                pass
            if f.read() == "0":
                f.write("1")

        df = pd.read_csv('server1.csv', index_col=0)
        self.curr_flight = df[df['flight_number'] == id]
        available_seats = df.loc[df['flight_number']
                                 == id, 'available_seats'][0]
        if available_seats > 0:
            print('inside if')
            self.history[-1]["status"] = "booked"
            if flight_class == "E":
                df.loc[df['flight_number'] == id,
                       'available_economy_seats'] -= 1
            else:
                df.loc[df['flight_number'] == id,
                       'available_business_seats'] -= 1
            df.loc[df['flight_number'] == id, 'available_seats'] = df.loc[df['flight_number'] == id,
                                                                          'available_economy_seats'] + df.loc[df['flight_number'] == id, 'available_business_seats']
            for i in range(1, 5):
                df.to_csv(f'server{i}.csv')
            # RELEASE DB ACCESS HERE
            with open('db_lock.txt', 'w') as f:
                f.write("0")
            return True
        else:
            # RELEASE DB ACCESS HERE
            with open('db_lock.txt', 'w') as f:
                f.write("0")
            return False


class Flight():
    def __init__(self, flight_number,
                 source, destination, time_of_flight, no_of_seats,
                 available_economy_seats, economy_price, business_price, airline):
        self.flight_number = flight_number
        self.source = source
        self.destination = destination
        self.time_of_flight = time_of_flight
        self.no_of_seats = no_of_seats
        self.available_economy_seats = available_economy_seats
        self.available_business_seats = self.no_of_seats - self.available_economy_seats
        self.available_seats = no_of_seats
        self.economy_price = economy_price
        self.business_price = business_price
        self.airline = airline

    def fillASeat(self, classs):
        if classs == "E":
            self.available_economy_seats -= 1
        else:
            self.available_business_seats -= 1
        self.available_seats = self.available_economy_seats + self.available_business_seats

    def __str__(self):
        return f"['flight_number': {self.flight_number}, 'source': {self.source}, 'destination': {self.destination}, 'time_of_flight': {self.time_of_flight}, 'no_of_seats': {self.no_of_seats}, 'available_economy_seats': {self.available_economy_seats}, 'economy_price': {self.economy_price}, 'business_price': {self.business_price}, 'airline': {self.airline}]"

# Static Data


user = User("admin")  # default user


def view_flights():  # Display flights in tabular format
    global df
    table = PrettyTable(
        [
            'flight_number', 'source', 'destination', 'time_of_flight', 'available_seats',
            'available_economy_seats', 'available_business_seats', 'economy_price', 'business_price', 'airline'
        ]
    )
    table.title = 'Flights'
    # d = []
    df = pd.read_csv('server2.csv', index_col=0)
    for i in range(len(df)):  # Storing the output tuples in table
        # f = flights[i]
        # row = [
        #         f.flight_number, f.source, f.destination, f.time_of_flight, f.available_seats,
        #         f.available_economy_seats, f.available_business_seats, f.economy_price, f.business_price, f.airline
        #     ]
        # d.append(row)
        table.add_row(df.iloc[i])
    # df = pd.DataFrame(data=d,columns=['flight_number', 'source', 'destination', 'time_of_flight', 'available_seats','available_economy_seats', 'available_business_seats', 'economy_price', 'business_price', 'airline'])
    # df.to_csv("server1.csv")
    return table.get_string()


def book_flight(id, flight_class):
    global df
    if id in df['flight_number'].unique():
        print('inside book_flight if')
        user.addToSeen(df[df['flight_number'] == id])
    else:
        return -1

    if flight_class == "B":
        print('inside B if')
        return int(user.curr_flight['business_price'].values[0])
    else:
        return int(user.curr_flight['economy_price'].values[0])


def pay(flight_class, id):
    return user.bookFlight(flight_class, id)


def getId():
    global clientList, clientId
    print(colored(f'Client List acquired : {clientList}', 'red'))
    client_mutex.acquire()
    clientId = 0 if len(clientList) == 0 else (max(clientList) + 1)
    clientList.append(clientId)
    client_mutex.release()
    print(colored(f'Client List released : {clientList}', 'red'))
    return clientId


def removeId(clientId):
    global clientList
    client_mutex.acquire()
    clientList.remove(clientId)
    client_mutex.release()


server.register_function(setServerClock)
server.register_function(getServerClock)
# server.register_function(get_flights)
server.register_function(pay)
server.register_function(book_flight)
server.register_function(view_flights)
server.register_function(requestCS)
server.register_function(getId)
server.register_function(removeId)
server.register_function(releaseCS)

server.register_function(sendVictory)
server.register_function(setCoordinator)
server.register_function(returnResponse)
server.register_function(doElection)

if __name__ == '__main__':
    try:
        print('Serving...')

        set_interval(serverSynchronize, rate)
        server.serve_forever()

    except KeyboardInterrupt:
        print('Exiting')
