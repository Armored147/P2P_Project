import grpc
import hashlib
from services import fileservice_pb2_grpc as pb2_grpc
from services import fileservice_pb2 as pb2
from concurrent import futures
import time
from services.file_service import FileService

class ChordNode:
    def __init__(self, ip, port, m=5):
        self.ip = ip
        self.port = port
        self.m = m
        self.id = self.hash_ip_port(ip, port)
        self.finger_table = [None] * m
        self.successor = None
        self.predecessor = None

    def hash_ip_port(self, ip, port):
        key = f"{ip}:{port}"
        hash_value = hashlib.sha1(key.encode()).hexdigest()
        return int(hash_value, 16) % (2 ** self.m)

    def find_successor(self, id):
        if self.successor and self.id < id <= self.successor.id:
            return self.successor
        else:
            closest_node = self.closest_preceding_node(id)
            if closest_node == self:
                return self.successor
            else:
                return closest_node.find_successor(id)

    def closest_preceding_node(self, id):
        for i in range(self.m - 1, -1, -1):
            if self.finger_table[i] and self.id < self.finger_table[i].id < id:
                return self.finger_table[i]
        return self

    def join(self, known_node):
        if known_node:
            self.predecessor = None
            self.successor = known_node.find_successor(self.id)
            self.fix_fingers()
            self.stabilize()
        else:
            self.predecessor = self
            self.successor = self
            for i in range(self.m):
                self.finger_table[i] = self

    def stabilize(self):
        if self.successor:
            x = self.successor.predecessor
            if x and self.id < x.id < self.successor.id:
                self.successor = x
            if self.successor != self:
                self.successor.notify(self)

    def notify(self, node):
        if not self.predecessor or (self.predecessor and self.id < node.id < self.predecessor.id):
            self.predecessor = node

    def fix_fingers(self):
        for i in range(self.m):
            start = (self.id + 2 ** i) % (2 ** self.m)
            self.finger_table[i] = self.find_successor(start)
        self.print_finger_table()

    def print_finger_table(self):
        print(f"Finger table for node {self.id}:")
        for i, node in enumerate(self.finger_table):
            if node:
                print(f"Entry {i}: Node ID {node.id}, Address: {node.ip}:{node.port}")
            else:
                print(f"Entry {i}: None")

    def start_server(self):
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        pb2_grpc.add_FileServiceServicer_to_server(FileService(), server)
        server.add_insecure_port(f"{self.ip}:{self.port}")
        server.start()
        print(f"Node {self.id} started on {self.ip}:{self.port}")
        self.print_finger_table()
        try:
            while True:
                self.stabilize()
                time.sleep(5)
        except KeyboardInterrupt:
            server.stop(0)
