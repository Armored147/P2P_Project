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
        print("Clean console")
        print("1. Print Finger Table")
        print("2. Predecessor")
        print("3. Successor")
        print("4. Check Health")
        print("6. Mostrar archivos")
        print("7. Subir archivo")
        print("8. Descargar archivo")
        print("9. Buscar archivo")
        print("0. Exit")
        choice = input("Enter your choice: ")
        if choice == '1':
            node.print_finger_table2()
        elif choice == '2':
            node.print_predecessor()
        elif choice == '3':
            node.print_successor()
        elif choice == '4':
            node.health_check()
        elif choice == '0':
            print("Exiting...")
            node.leave_network()
            node.stop_server()
            break
        elif choice == 'cl':
            system('clear')
        elif choice == '6':
            node.show_files()
        elif choice == '7':
            filename = input("Ingrese el nombre del archivo para subir: ")
            node.upload_file(filename)
        elif choice == '8':
            file_id = int(input("Ingrese el ID del archivo a descargar: "))
            node.download_file(file_id)  
        elif choice == '9':  # Implementa la búsqueda de archivo
            file_id = int(input("Ingrese el ID del archivo a buscar: "))
            node.search_file(file_id)
        else:
            print("Invalid choice. Please try again.")
        

if __name__ == "__main__":
    ip = str(sys.argv[1])
    port = int(sys.argv[2])
    
    if len(sys.argv) == 5:
        known_ip = str(sys.argv[3])
        known_port = int(sys.argv[4])
        run_node(ip, port, known_ip, known_port)
    else:
        run_node(ip, port)
