from xmlrpc.client import ServerProxy
import socket

#proxy = ServerProxy("http://localhost:8888")

if __name__ == "__main__":
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('localhost', 8888))
    while True:
        print("\nMenu:")
        print("1. View Tickets")
        print("2. Book Tickets")
        print("3. Exit")
        choice = input("Enter your choice: ")
        if choice == '1':
            client.send('menu'.encode())
            menu = client.recv(16384).decode()
            print("\nMenu:")
            print(menu)
        elif choice == '2':
            id = input("Enter flight ID to book your flight:").strip()
            flight_class = (
                input("Choose flight class (B-business, E-economy):").strip().upper()
            )
            client.send(f'add_'.encode())
            response = client.recv(1024).decode()
            print(response)
        elif choice == '3':
            client.send('view_cart'.encode())
            cart = client.recv(1024).decode()
            print("\nCart:")
            print(cart)
        elif choice == '4':
            client.send('exit'.encode())
            response = client.recv(1024).decode()
            print(response)
            break
        else:
            print("Invalid choice. Try again.")
