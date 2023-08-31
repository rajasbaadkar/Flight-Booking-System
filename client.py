from termcolor import colored
from xmlrpc.client import ServerProxy
from prettytable import PrettyTable
import threading
import os
import sys
os.system('color')

clientID = 0
balancer_port = 3500
proxy = ServerProxy(f'http://localhost:{balancer_port}')
mutex = threading.Lock()
rate = 7  # Default rate 7 sec
clock = 0

def exit_handler():
    proxy.removeId(clientID)

def set_interval(func, sec):
    def func_wrapper():
        set_interval(func, sec)
        func()
    t = threading.Timer(sec, func_wrapper)
    t.start()
    return t


def clientSynchronize():
    global clock
    mutex.acquire()  # Keep increasing at "rate", keeping in mind race around condition
    clock += 1
    mutex.release()
    # print(colored(f"\n[INFO] Client Logical Clock(Updated at interval set): {clock}\n", 'yellow'))


# Lamport's Algorithm

def setClientClock(server_clock):  # Client receives message from server
    global clock
    print(colored(
        f"\n[INFO] Before client recieves message: Client Logical Clock = {clock}\n", 'yellow'))
    if server_clock > clock:
        mutex.acquire()
        clock = server_clock + 1  # Send clock + 1 by default from client side
        mutex.release()
    print(colored(
        f"\n[INFO] After client recieves message: Client Logical Clock = {clock}\n", 'yellow'))


def synchronize(func, *args):  # Synchronizes server and client clocks before an event
    proxy.setServerClock(clock)  # Synchronise with server
    if args:
        result = func(*args)
    else:
        result = func()
    # Update the client clock after the function call
    setClientClock(proxy.getServerClock())
    return result

def synchronizeCS(func, *args):  # Synchronizes server and client clocks before an event
    reply = False  # Synchronise with server, requestServer() => send clock and request CS 
    while not reply:
        reply = proxy.requestCS(clock, clientID)
    if args:
        result = func(*args)
    else:
        result = func() # Critical section
    # Update the client clock after the function call
    setClientClock(proxy.releaseCS(clock, clientID))
    return result

if __name__ == '__main__':
    t = set_interval(clientSynchronize, rate)
    i = synchronize(proxy.get_server)
    proxy = ServerProxy(f'http://localhost:{i}')
    clientID = proxy.getId() # call the clientID function here => assign_ID and store in server as well as in client
    print(f"Accessing resources from server {i}...")
    while True:
        print('\nGetting Flight Data...')
        synchronize(proxy.view_flights)  # Synchronize
        print('''
        Choices available:
        1. View Flights
        2. Book a Flight
        3. Exit
        '''
              )
        print("Enter your choice: ", end='')
        choice = int(input())
        if choice == 1:
            print(synchronize(proxy.view_flights))  # Synchronize
        elif choice == 2:
            id = input('Enter flight ID to book your flight: ').strip()
            flight_class = input(
                'Choose flight class (B-business, E-economy): ').strip().upper()
            cost = synchronizeCS(proxy.book_flight, id,
                               flight_class)  # Synchronize
            if input(f"Cost of flight - Rs. {cost}\nPay to book? [Y/N]: ").upper()[0] == 'Y':
                synchronizeCS(proxy.pay, flight_class, id)  # Synchronize pay()
                print("Your flight has been booked")
            else:
                print("You have cancelled your booking :(")
        elif choice == 3:
            print('Thank you for using this app :)')
            t.cancel()
            break
        else:
            print("You have entered a wrong choice.")
