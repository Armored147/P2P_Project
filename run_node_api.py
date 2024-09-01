from flask import Flask, request, jsonify, Response, current_app
from services.chordNode import ChordNode
import threading
import time
import sys
import os
import signal

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
        finger_table = node.get_finger_table()
        return jsonify({"finger_table": finger_table, "message": "Finger table printed",}), 200
    return jsonify({"error": "Node not initialized"}), 400

@app.route('/get_predecessor', methods=['GET'])
def get_predecessor():
    if node:
        predecessor = node.print_predecessor()
        return jsonify({"predecessor": predecessor}), 200
    return jsonify({"error": "Node not initialized"}), 400

@app.route('/get_successor', methods=['GET'])
def get_successor():
    if node:
        successor = node.print_successor()
        return jsonify({"successor": successor}), 200
    return jsonify({"error": "Node not initialized"}), 400

@app.route('/show_files', methods=['GET'])
def show_files():
    if node:
        response, files = node.show_files()
        return jsonify({"message": response, "list of files":files}), 200
    return jsonify({"error": "Node not initialized"}), 400

@app.route('/upload_file', methods=['POST'])
def upload_file():
    if node:
        data = request.get_json()
        filename = data.get("filename")
        if not filename:
            return jsonify({"error": "Filename not provided"}), 400
        response, files = node.upload_file(filename)
        return jsonify({"message": response, "list of files":files}), 200
    return jsonify({"error": "Node not initialized"}), 400

@app.route('/download_file', methods=['POST'])
def download_file():
    if node:
        data = request.get_json()
        filename = data.get("filename")
        if not filename:
            return jsonify({"error": "Filename not provided"}), 400
        response = node.download_file(filename)
        return jsonify({"message": response}), 200
    return jsonify({"error": "Node not initialized"}), 400

@app.route('/search_file', methods=['POST'])
def search_file():
    if node:
        data = request.get_json()
        filename = data.get("filename")
        if not filename:
            return jsonify({"error": "Filename not provided"}), 400
        response = node.search_file(filename)
        return jsonify({"message": response}), 200
    return jsonify({"error": "Node not initialized"}), 400

@app.route('/repair', methods=['GET'])
def repair():
    node.stabilize()
    node.fix_fingers()
    return jsonify({"message": "Server repairing..."}), 200

@app.route('/shutdown', methods=['GET'])
def shutdown():
    shutdown_server()
    return jsonify({"message": "Server shutdown..."}), 200
    
def shutdown_server():
    node.leave_network()
    node.stop_server()
    pid = os.getpid()  # Obtener el PID del proceso actual
    os.kill(pid, signal.SIGINT)  # Enviar la señal SIGINT al proceso

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
