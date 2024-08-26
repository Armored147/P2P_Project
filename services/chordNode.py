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
        if self.successor and (
                (self.id < id <= self.successor.id) or
                (self.id > self.successor.id and (id > self.id or id < self.successor.id))):
            return self.successor
        else:
            closest_node = self.closest_preceding_node(id)
            if closest_node == self:
                return self.successor
            else:
                with grpc.insecure_channel(f'{closest_node.ip}:{closest_node.port}') as channel:
                    stub = pb2_grpc.FileServiceStub(channel)
                    response = stub.FindSuccessor(pb2.FindSuccessorRequest(id=id))
                    return ChordNode(response.ip, response.port, m=self.m)

    def closest_preceding_node(self, id):
        for i in range(self.m - 1, -1, -1):
            if self.finger_table[i] and (
                    (self.id < self.finger_table[i].id < id) or
                    (self.id > self.finger_table[i].id and self.finger_table[i].id < id) or
                    (self.id < self.finger_table[i].id and self.finger_table[i].id > id)):
                return self.finger_table[i]
        return self

    def join(self, known_ip=None, known_port=None):
        if known_ip and known_port:
            print(f"Node {self.id} trying to join the network via node at {known_ip}:{known_port}")
            with grpc.insecure_channel(f'{known_ip}:{known_port}') as channel:
                stub = pb2_grpc.FileServiceStub(channel)
                response = stub.FindSuccessor(pb2.FindSuccessorRequest(id=self.id))
                self.successor = ChordNode(response.ip, response.port, m=self.m)
                self.predecessor = None
                if self.successor:
                    print(f"Node {self.id} joined with successor {self.successor.id}")
                    self.stabilize()
                    self.fix_fingers()
                else:
                    print(f"Node {self.id} could not find a valid successor")
        else:
            print(f"Node {self.id} is the only node in the network")
            self.predecessor = self
            self.successor = self
            for i in range(self.m):
                self.finger_table[i] = self

    def stabilize(self):
        if self.successor:
            try:
                with grpc.insecure_channel(f'{self.successor.ip}:{self.successor.port}') as channel:
                    stub = pb2_grpc.FileServiceStub(channel)
                    response = stub.GetPredecessor(pb2.Empty())
                    if response.ip and response.ip != self.ip:
                        x = ChordNode(response.ip, response.port, m=self.m)
                        if ((self.id < x.id < self.successor.id) or
                            (self.id > self.successor.id and (x.id > self.id or x.id < self.successor.id))):
                            self.successor = x
                    self.successor.notify(self)
            except grpc.RpcError as e:
                print(f"Stabilization failed with error: {e}")
        else:
            print(f"No successor found for Node {self.id}. Retrying stabilization.")

    def notify(self, node):
        if not self.predecessor or (
                (self.predecessor and (self.predecessor.id > self.id and node.id < self.predecessor.id)) or
                (self.predecessor and self.predecessor.id < self.id and node.id > self.predecessor.id)):
            self.predecessor = node

    def fix_fingers(self):
        for i in range(self.m):
            start = (self.id + 2 ** i) % (2 ** self.m)
            self.finger_table[i] = self.find_successor(start)

    def print_finger_table(self):
        print(f"Finger table for node {self.id}:")
        for i, entry in enumerate(self.finger_table):
            if entry:
                print(f"Entry {i}: Node ID {entry.id}, Address: {entry.ip}:{entry.port}")
            else:
                print(f"Entry {i}: None")

    def start_server(self):
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        pb2_grpc.add_FileServiceServicer_to_server(FileService(self), server)
        server.add_insecure_port(f"{self.ip}:{self.port}")
        server.start()
        try:
            while True:
                self.stabilize()
                self.fix_fingers()
                time.sleep(5)
        except KeyboardInterrupt:
            server.stop(0)
