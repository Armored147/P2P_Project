from os import system
import sys
import threading
import time
from services.chordNode import ChordNode

def run_node(ip, port, known_ip=None, known_port=None):
    node = ChordNode(ip, port)

    # Start the server in a separate thread
    server_thread = threading.Thread(target=node.start_server)
    server_thread.daemon = True  # This ensures the thread will close when the main program exits
    server_thread.start()

    # Give the server some time to start
    time.sleep(1)

    if known_ip and known_port:
        print(f"Attempting to connect to known node at {known_ip}:{known_port}")
        node.join(known_ip, known_port)
    else:
        print("No known node provided, this will be the first node in the network.")
        node.join()


    # NOTA: El gRPC no puede con mas de 4 nodos 

    # Menu loop
    while True:
        print("\nMenu:")
        print("0. Clean console")
        print("1. Print Finger Table")
        print("2. Predecessor")
        print("3. Successor")
        print("4. Check Health")
        print("5. Exit")
        choice = input("Enter your choice: ")
        if choice == '1':
            node.print_finger_table2()
        elif choice == '2':
            node.print_predecessor()
        elif choice == '3':
            node.print_successor()
        elif choice == '4':
            node.health_check()
        elif choice == '5':
            print("Exiting...")
            node.leave_network()
            node.stop_server()
            break
        elif choice == '0':
            system('cls')
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    ip = sys.argv[1]
    port = int(sys.argv[2])

    if len(sys.argv) == 5:
        known_ip = sys.argv[3]
        known_port = int(sys.argv[4])
        run_node(ip, port, known_ip, known_port)
    else:
        run_node(ip, port)
