import json
import socket


# if __name__ == "__main__":
#     while True:
#         print(
#             """
#             Choices available:
#             1. View Flights
#             2. Book a Flight
#             3. Exit
#             """
#         )
#         print("Enter your choice: ", end="")
#         choice = int(input())
#         if choice == 1:
#             flights = proxy.view_flights()  # Call the server's view_flights() method
#             print(flights)
#         elif choice == 2:
#             id = input("Enter flight ID to book your flight:").strip()
#             flight_class = (
#                 input("Choose flight class (B-business, E-economy):").strip().upper()
#             )
#             cost = proxy.bookFlight(id, flight_class)  # Call the server's book_flight() method
#             if (
#                 input(f"Cost of flight - Rs. {cost}\nPay to book? [Y/N]: ").upper()[0]
#                 == "Y"
#             ):
#                 proxy.pay(flight_class)  # Call the server's pay() method
#                 print("Your flight has been booked")
#             else:
#                 print("You have canceled your booking :(")
#         elif choice == 3:
#             print("Thank you for using this app :)")
#             break
#         else:
#             print("You have entered a wrong choice.")

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
            params = {
                "type":"menu"
            }
            params_json = json.dumps(params)
            client.send(params_json.encode('utf-8'))
            menu = client.recv(1024).decode()
            print("\nMenu:")
            print(menu)
        elif choice == '2':
            id = input("Enter flight ID to book your flight:").strip()
            flight_class = (
                input("Choose flight class (B-business, E-economy):").strip().upper()
            )
            params = {
                "type":"book",
                "id":id,
                "class":flight_class
            }
            params_json = json.dumps(params)
            client.send(params_json.encode('utf-8'))
            cost = client.recv(1024).decode()
            if (
                input(f"Cost of flight - Rs. {cost}\nPay to book? [Y/N]: ").upper()[0]
                == "Y"
            ):
                print("Your flight has been booked")
        elif choice == '3':
            params = {
                "type":"exit"
            }
            params_json = json.dumps(params)
            client.send(params_json.encode('utf-8'))
            client.send('exit'.encode())
            response = client.recv(1024).decode()
            print(response)
            break
        else:
            print("Invalid choice. Try again.")
