from xmlrpc.server import SimpleXMLRPCServer
import xmlrpc.client
import os
import string
import random
from datetime import datetime
from prettytable import PrettyTable
import threading

# Model classes
def rajas():
    class User:
        def __init__(self, username):
            self.username = username  # User Identification information
            self.history = []  # Contain the list of flights, along with booked status
            self.curr_flight = None  # Contains the active flights if any

        def __str__(self):
            return f"['username': {self.username}, 'history': {self.history}, 'curr_flight': {self.curr_flight}]"

        def addToSeen(self, f):
            self.history.append({"flight": f.flight_number, "status": "seen"})
            self.curr_flight = f

        def bookFlight(self, flight_class):
            self.history[-1]["status"] = "booked"
            self.curr_flight.fillASeat(flight_class)

    class Flight:
        def __init__(
            self,
            flight_number,
            source,
            destination,
            time_of_flight,
            no_of_seats,
            available_economy_seats,
            economy_price,
            business_price,
            airline,
        ):
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

        def fillASeat(self, flight_class):
            if flight_class == "E":
                self.available_economy_seats -= 1
            else:
                self.available_business_seats -= 1
                self.available_seats = (
                    self.available_economy_seats + self.available_business_seats
                )

        def __str__(self):
            return f"['flight_number': {self.flight_number}, 'source': {self.source}, 'destination': {self.destination}, 'time_of_flight': {self.time_of_flight}, 'no_of_seats': {self.no_of_seats}, 'available_economy_seats': {self.available_economy_seats}, 'economy_price': {self.economy_price}, 'business_price': {self.business_price}, 'airline': {self.airline}]"

    # Static Data

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
    cities = ["Mumbai", "Pune", "New Delhi", "Bangalore", "Chennai", "Kolkata"]
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
        flights.append(
            Flight(
                flight_number="".join(
                    random.choices(string.ascii_letters + string.digits, k=6)
                ),
                source=c[0],
                destination=c[1],
                time_of_flight=random.choice(times),
                no_of_seats=random.randint(200, 300),
                available_economy_seats=random.randint(150, 200),
                economy_price=airline["cost_e"],
                business_price=airline["cost_b"],
                airline=airline["name"],
            )
        )

    # Custom Server-side functions

    def get_flights():  # Returns list of Flight objects to the client terminal using pretty table
        return flights

    def view_flights():  # Display flights in tabular format
        table = PrettyTable(
            [
                "flight_number",
                "source",
                "destination",
                "time_of_flight",
                "available_seats",
                "available_economy_seats",
                "available_business_seats",
                "economy_price",
                "business_price",
                "airline",
            ]
        )
        table.title = "Flights"
        for i in range(len(flights)):  # Storing the output tuples in table
            f = flights[i]
            table.add_row(
                [
                    f.flight_number,
                    f.source,
                    f.destination,
                    f.time_of_flight,
                    f.available_seats,
                    f.available_economy_seats,
                    f.available_business_seats,
                    f.economy_price,
                    f.business_price,
                    f.airline,
                ]
            )
        return table.get_string()

    def bookFlight(id, flight_class):
        for f in flights:
            if f.flight_number == id:
                user.addToSeen(f)
                break

        if flight_class == "B":
            return user.curr_flight.business_price
        else:
            return user.curr_flight.economy_price

    def pay(flight_class):
        user.bookFlight(flight_class)


    # def handle_client(client):
    #     try:
    #         client_thread_id = threading.get_ident()  
    #         print(f"Thread {client_thread_id} handling a client connection")

    #         # while True:
    #         #     client_request = client.recv(1024).decode("utf-8")
    #         #     if not client_request:
    #         #         break    
    #         #print(f"Thread {client_thread_id} closed the client connection")

    #     except Exception as e:
    #         print(f"Error: {e}")
    #     finally:
    #         client.close()


    server.register_function(get_flights)
    server.register_function(pay)
    server.register_function(bookFlight)
    server.register_function(view_flights)

server = SimpleXMLRPCServer(("localhost", 3000), allow_none=True)

if __name__ == "__main__":
    try:
        print("Serving...")
        thread_counter = 0  # Initialize a thread counter
        
        while True:
            client_sock, client_addr = server.socket.accept()
            print(client_sock,client_addr)
            # Create a new thread for each client
            client_thread = threading.Thread(target=rajas, args=())
            client_thread.start()
            #client_thread.join()

            thread_counter += 1  # Increment the thread counter
            print(f"Started Thread {client_thread.ident} for Client {thread_counter}")
            
            server.serve_forever()

    except KeyboardInterrupt:
        print("Exiting")

def run_server():
    # Create a SimpleXMLRPCServer
    server = SimpleXMLRPCServer(("localhost", 3000), allow_none=True)
    
    # Register your XML-RPC methods
    server.register_function(get_flights)
    server.register_function(pay)
    server.register_function(bookFlight)
    server.register_function(view_flights)
    print("Server is running...")
    
    try:
        while True:
            # Accept incoming client connections
            client_socket, _ = server.socket.accept()
            
            # Create a new thread to handle the client request
            client_thread = threading.Thread(target=rajas, args=())
            client_thread.start()
            
    except KeyboardInterrupt:
        print("Server is stopping...")

if __name__ == "__main__":
    run_server()
