import sys
from services.chordNode import ChordNode

if __name__ == "__main__":
    ip = sys.argv[1]
    port = int(sys.argv[2])
    known_node_address = sys.argv[3] if len(sys.argv) > 3 else None

    node = ChordNode(ip, port)

    if known_node_address:
        known_ip, known_port = known_node_address.split(":")
        known_node = node.find_successor(node.hash_ip_port(known_ip, int(known_port)))
        node.join(known_node)
    else:
        node.join(None)

    node.start_server()
