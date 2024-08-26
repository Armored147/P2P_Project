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

    # Menu loop
    while True:
        print("\nMenu:")
        print("1. Print Finger Table")
        print("2. Exit")
        choice = input("Enter your choice: ")
        if choice == '1':
            node.print_finger_table()
        elif choice == '2':
            print("Exiting...")
            break
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
