from flask import Flask, request, jsonify
from services.chordNode import ChordNode
import threading
import time
import sys

app = Flask(__name__)
node = None

def initialize_node(ip, port, known_ip=None, known_port=None):
    global node
    node = ChordNode(ip, port)
    
    # Start the server in a separate thread
    server_thread = threading.Thread(target=node.start_server)
    server_thread.daemon = True  # This ensures the thread will close when the main program exits
    server_thread.start()
    
    # Give the server some time to start
    time.sleep(1)
    
    if known_ip and known_port:
        node.join(known_ip, known_port)
    else:
        node.join()


@app.route('/finger_table', methods=['GET'])
def print_finger_table():
    if node:
        node.print_finger_table2()
        return jsonify({"message": "Finger table printed"}), 200
    return jsonify({"error": "Node not initialized"}), 400


# Aceptar parámetros desde la línea de comandos
if __name__ == "__main__":
    ip = str(sys.argv[1])
    port = int(sys.argv[2])
    
    if len(sys.argv) == 5:
        known_ip = str(sys.argv[3])
        known_port = int(sys.argv[4])
        initialize_node(ip, port, known_ip, known_port)
    else:
        initialize_node(ip, port)
    
    app.run(host="0.0.0.0", port=5000)
