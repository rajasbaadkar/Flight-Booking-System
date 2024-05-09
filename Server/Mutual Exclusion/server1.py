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
queue = []  # Waitlist of clientId requesting CS
queue_mutex = threading.Lock()
clientList = []  # List of clientIds
clientId = 0
server = SimpleXMLRPCServer(('localhost', 3000), allow_none=True)
client_mutex = threading.Lock()
critical_mutex = threading.Lock()


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
    # print(colored(f"\n[INFO] Server Logical Clock(Updated atinterval set): {clock}\n", 'yellow'))

# Lamport's Algorithm


def getServerClock():  # Server sends message to client
    return clock

def setServerClock(client_clock):  # Server receives message from client
    global clock
    print(colored(
        f"\n[INFO] Before server receives message: Server Logical Clock = {clock}\n", 'yellow'))
    if client_clock > clock:
        mutex.acquire()
        clock = client_clock + 1  # Send clock + 1 by default from client side
        mutex.release()
    print(colored(
        f"\n[INFO] After server receives message: Server Logical Clock = {clock}\n", 'yellow'))

# Mutual Exclusion using Centralized Algorithm

def requestCS(client_clock, clientID):  # Server receives message from client
    global clock, critical_mutex, queue
    print(colored(
        f"\n[INFO] Before server receives message: Server Logical Clock = {clock}\n", 'yellow'))
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
                f"\n[INFO] After server receives message: Server Logical Clock = {clock}\n", 'yellow'))

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
        f"\n[INFO] Before server receives message: Server Logical Clock = {clock}\n", 'yellow'))
    if client_clock > clock:
        mutex.acquire()
        clock = client_clock + 1  # Send clock + 1 by default from client side
        mutex.release()
    print(colored(
        f"\n[INFO] After server receives message: Server Logical Clock = {clock}\n", 'yellow'))
    critical_mutex.release()
    print(colored(f"\nCritical Mutex Released by {clientID}", "red"))
    return clock

# MODEL CLASSES

class User():
    def __init__(self, username):
        self.username = username  # User Identification information
        self.history = []  # Contain the list of flights, along with booked status
        self.curr_flight = None  # Contains the active flights if any

    def __str__(self):
        return f"['username': {self.username}, 'history': {self.history},'curr_flight':{self.curr_flight}]"

    def addToSeen(self, f):
        self.history.append({"flight": f.flight_number, "status": "seen"})
        self.curr_flight = f

    def bookFlight(self, flight_class):
        if self.curr_flight.available_seats > 0:
            self.history[-1]["status"] = "booked"
            self.curr_flight.fillASeat(flight_class)
            return True
        else:
            return False


class Flight():
    def __init__(self, flight_number, source, destination, time_of_flight, no_of_seats, available_economy_seats, economy_price, business_price, airline):
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
        return f"['flight_number': {self.flight_number}, 'source': {self.source},'destination': {self.destination}, 'time_of_flight': {self.time_of_flight},'no_of_seats': {self.no_of_seats},'available_economy_seats':{self.available_economy_seats}, 'economy_price':{self.economy_price},'business_price': {self.business_price}, 'airline': {airline}]"

# STATIC DATA

airlines = [
    {
        "name": "British Airways",
        "cost_b": random.randint(100000, 200000),
        "cost_e": random.randint(10000, 20000),
    },
    {
        "name": "Air India",
        "cost_b": random.randint(100000, 200000),
        "cost_e": random.randint(10000, 20000),
    },
    {
        "name": "SpiceJet",
        "cost_b": random.randint(100000, 200000),
        "cost_e": random.randint(10000, 20000),
    },
    {
        "name": "Jet Airways",
        "cost_b": random.randint(100000, 200000),
        "cost_e": random.randint(10000, 20000),
    },
]

cities = ['Mumbai', 'Pune', 'New Delhi', 'Bangalore', 'Chennai', 'Kolkata']

times = [
    datetime.strptime("13 Sep 2023", "%d %b %Y").replace(hour=9, minute=00),
    datetime.strptime("15 Sep 2023", "%d %b %Y").replace(hour=12, minute=00),
    datetime.strptime("16 Nov 2023", "%d %b %Y").replace(hour=15, minute=00),
    datetime.strptime("13 Oct 2023", "%d %b %Y").replace(hour=18, minute=00),
    datetime.strptime("28 Sep 2023", "%d %b %Y").replace(hour=21, minute=00),
]

flights = []  # list of randomly generated flights
user = User("admin")  # default user

for i in range(6):
    c = random.sample(cities, 2)
    airline = random.choice(airlines)
    flights.append(Flight(
        flight_number=''.join(random.choices(
            string.ascii_letters + string.digits, k=6)),
        source=c[0],
        destination=c[1],
        time_of_flight=random.choice(times),
        no_of_seats=random.randint(1, 2),
        available_economy_seats=random.randint(150, 200),
        economy_price=airline['cost_e'],
        business_price=airline['cost_b'],
        airline=airline['name']
    ))


def get_flights():  # Returns list of Flight objects to the client terminal using pretty table
    return flights


def view_flights():  # Display flights in tabular format
    table = PrettyTable(
        [
            'flight_number', 'source', 'destination', 'time_of_flight',
            'available_seats',
            'available_economy_seats', 'available_business_seats',
            'economy_price', 'business_price', 'airline'
        ]
    )
    table.title = 'Flights'
    for i in range(len(flights)):  # Storing the output tuples in table
        f = flights[i]
        table.add_row(
            [
                f.flight_number, f.source, f.destination, f.time_of_flight,
                f.available_seats,
                f.available_economy_seats, f.available_business_seats,
                f.economy_price, f.business_price, f.airline
            ]
        )
        return table.get_string()


def book_flight(id, flight_class):
    for f in flights:
        if f.flight_number == id:
            user.addToSeen(f)
            break
        else:
            return -1
    if flight_class == "B":
        return user.curr_flight.business_price
    else:
        return user.curr_flight.economy_price


def pay(flight_class):
    return user.bookFlight(flight_class)


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
server.register_function(get_flights)
server.register_function(pay)
server.register_function(book_flight)
server.register_function(view_flights)
server.register_function(requestCS)
server.register_function(getId)
server.register_function(removeId)
server.register_function(releaseCS)

if __name__ == '__main__':
    try:
        print('Serving...')
        set_interval(serverSynchronize, rate)
        server.serve_forever()
    except KeyboardInterrupt:
        print('Exiting')