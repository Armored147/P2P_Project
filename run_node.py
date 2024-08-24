import sys
from services.chordNode import ChordNode

def run_node(ip, port, known_ip=None, known_port=None):
    node = ChordNode(ip, port)

    if known_ip and known_port:
        # Conectarse al nodo conocido usando gRPC
        print(f"Attempting to connect to known node at {known_ip}:{known_port}")
        node.join_known(known_ip, known_port)
    else:
        # Si no hay nodo conocido, el nodo se considera el único en la red
        print("No known node provided, this will be the first node in the network.")
        node.join(None)

    # Ahora que el nodo está configurado, inicia el servidor
    node.start_server()

if __name__ == "__main__":
    ip = sys.argv[1]
    port = int(sys.argv[2])

    if len(sys.argv) == 5:
        known_ip = sys.argv[3]
        known_port = int(sys.argv[4])
        run_node(ip, port, known_ip, known_port)
    else:
        run_node(ip, port)
