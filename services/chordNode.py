import grpc
import hashlib
from services import fileservice_pb2_grpc as pb2_grpc
from . import fileservice_pb2 as pb2
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
    
    def join(self, known_ip, known_port):
        if known_ip != None and known_port != None:
            print(f"Node {self.id} trying to join the network")
            with grpc.insecure_channel(f'{known_ip}:{known_port}') as channel:
                stub = pb2_grpc.FileServiceStub(channel)
                response = stub.FindSuccessor(pb2.FindSuccessorRequest(id=self.id))
                self.predecessor = None
                self.successor = ChordNode(response.ip, response.port, m=self.m)
                print("Joining the process")
                if self.successor:
                    print(f"Node {self.id} joined with successor {self.successor.id}")
                    self.stabilize()
                    self.fix_fingers()
                else:
                    print(f"Node {self.id} could not find a valid successor")
        else:
            self.predecessor = None
            self.successor = self
            for i in range(self.m):
                self.finger_table[i] = self
            print(f"Node {self.id} is the only node in the network")

    def find_successor(self, id):
        if self.successor and (self.id < id <= self.successor.id or 
        (self.id > self.successor.id and (id > self.id or id <= self.successor.id))):
            print(f"Node {self.id} found successor {self.successor.id} for id {id}")
            return self.successor
        else:
            closest_node = self.closest_preceding_node(id)
            if closest_node == self:
                print(f"Node {self.id} is returning itself as successor for id {id}")
                return self.successor
            else:
                print(f"Node {self.id} forwarding request to {closest_node.id} at {closest_node.ip}:{closest_node.port}")
                with grpc.insecure_channel(f'{closest_node.ip}:{closest_node.port}') as channel:
                    stub = pb2_grpc.FileServiceStub(channel)
                    try:
                        response = stub.FindSuccessor(pb2.FindSuccessorRequest(id=id))
                        print(f"Node {self.id} received successor {response.id} from node {closest_node.id}")
                        return ChordNode(response.ip, response.port, m=self.m)
                    except grpc.RpcError as e:
                        print(f"RPC failed with error: {e}")
                        return None

    def closest_preceding_node(self, id):
        for i in range(self.m - 1, -1, -1):
            if self.finger_table[i]:
                node_id = self.finger_table[i].id
                if self.id < node_id < id or (self.id > id and (node_id > self.id or node_id < id)):
                    return self.finger_table[i]
        return self


    def stabilize(self):
        if self.successor and self.successor != self:
            with grpc.insecure_channel(f'{self.successor.ip}:{self.successor.port}') as channel:
                stub = pb2_grpc.FileServiceStub(channel)
                response = stub.GetPredecessor(pb2.Empty())
                
                if response.id != 0 and response.id != self.id:
                    self.successor = ChordNode(response.ip, response.port, m=self.m)
                
                # Notifica al sucesor actual sobre este nodo
                stub.Notify(pb2.NotifyRequest(ip=self.ip, port=self.port, id=self.id))


    def notify(self, ip, port, id):
        if not self.predecessor or (self.predecessor and self.id < id < self.predecessor.id):
            self.predecessor = ChordNode(ip, port, m=self.m)


    def fix_fingers(self):
        for i in range(self.m):
            start = (self.id + 2 ** i) % (2 ** self.m)
            print(f"Start: {start}")
            successor = self.find_successor(start)
            self.finger_table[i] = successor
        self.print_finger_table()

# --------------------------------------------------------------------------------------------

    def print_finger_table(self):
        print(f"Finger table for node {self.id}:")
        for i, node in enumerate(self.finger_table):
            if node:
                print(f"Entry {i}: Node ID {node.id}, Address: {node.ip}:{node.port}")
            else:
                print(f"Entry {i}: None")

# --------------------------------------------------------------------------------------------

    def start_server(self):
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        pb2_grpc.add_FileServiceServicer_to_server(FileService(self), server)
        server.add_insecure_port(f"{self.ip}:{self.port}")
        server.start()
        print(f"Node {self.id} started on {self.ip}:{self.port}")
        try:
            while True:
                self.stabilize()
                self.fix_fingers()
                time.sleep(5)  
        except KeyboardInterrupt:
            server.stop(0)




"""     def join_known(self, known_ip, known_port):
        print(f"Connecting to known node at {known_ip}:{known_port}")
        with grpc.insecure_channel(f'{known_ip}:{known_port}') as channel:
            stub = pb2_grpc.FileServiceStub(channel)
            response = stub.FindSuccessor(pb2.FindSuccessorRequest(id=self.id))
            self.successor = ChordNode(response.ip, response.port, m=self.m)
            print(f"Joined network via node {response.id}, set as successor.")
            self.fix_fingers()
            self.stabilize() """