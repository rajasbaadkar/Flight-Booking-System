from termcolor import colored
from xmlrpc.client import ServerProxy
from prettytable import PrettyTable
import threading
import os
import sys
os.system('color')


proxy = ServerProxy('http://localhost:3000')
mutex = threading.Lock()
rate = 7
clock = 0 #Default rate 7 sec


def set_interval(func, sec):
    def func_wrapper():
        set_interval(func, sec)
        func()
    t = threading.Timer(sec, func_wrapper)
    t.start()
    return t


def clientSynchronize():
    global clock
    mutex.acquire() # Keep increasing at "rate", keeping in mind race around condition
    clock += 1
    mutex.release()
    print(colored(f"\n[INFO] Client Logical Clock(Updated at interval set):{clock}\n", 'yellow'))



# LAMPORT'S ALGORITHM
def setClientClock(server_clock): # Client receives message from server
    global clock
    print(colored(f"\n[INFO] Before client receives message: Client Logical Clock = {clock}\n",'yellow'))
    if server_clock > clock:
        mutex.acquire()
        clock = server_clock + 1 # Send clock + 1 by default from client side
        mutex.release()
    print(colored(f"\n[INFO] After client receives message: Client Logical Clock = {clock}\n",'yellow'))


def synchronize(func, *args): # Synchronizes server and client clocks before an event
    proxy.setServerClock(clock) # Synchronise with server
    if args:
        result = func(*args)
    else:
        result = func()

    # Update the client clock after the function call
    setClientClock(proxy.getServerClock())
    return result


if __name__ == '__main__':
    t = set_interval(clientSynchronize, rate)
    while True:
        print('\nGetting Flight Data...')
        flights = synchronize(proxy.get_flights) # Synchronize
        print(
            '''
            Choices available:
            1. View Flights
            2. Book a Flight
            3. Exit
            '''
        )
        print("Enter your choice: ", end='')
        choice = int(input())
        if choice == 1:
            print(synchronize(proxy.view_flights)) # Synchronize
        elif choice == 2:
            id = input('Enter flight ID to book your flight:').strip()
            flight_class = input('Choose flight class (B-business, E-economy): ').strip().upper()
            cost = synchronize(proxy.book_flight, id, flight_class)
            if input(f"Cost of flight - Rs. {cost}\nPay to book?[Y/N]: ").upper()[0] == 'Y':
                # Synchronizepay()
                synchronize(proxy.pay, flight_class)
                print("Your flight has been booked")
            else:
                print("You have cancelled your booking :(")
        elif choice == 3:
            print('Thank you for using this app :)')
            t.cancel()
            break
        else:
            print("You have entered a wrong choice.")