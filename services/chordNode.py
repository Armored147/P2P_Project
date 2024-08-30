import grpc
import hashlib
from concurrent import futures
import time
from tabulate import tabulate
from services import fileservice_pb2_grpc as pb2_grpc
from . import fileservice_pb2 as pb2
from services.file_service import FileService
from grpc_health.v1 import health
from grpc_health.v1 import health_pb2
from grpc_health.v1 import health_pb2_grpc

class ChordNode:
    def __init__(self, ip, port, m=5):
        self.ip = ip
        self.port = port
        self.m = m
        self.id = self.hash_ip_port(ip, port)
        self.finger_table = []
        
        for i in range(m):
            entry = {
                'start': (self.id + 2**i) % 2**m,  # Cálculo de la posición
                'interval': ((self.id + 2**i) % 2**m, (self.id + 2**(i+1)) % 2**m),  # Intervalo que cubre esta entrada
                'successor': None  # Sucesor responsable de este intervalo
            }
            self.finger_table.append(entry)
        
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
            successor = self.finger_table[i]['successor']
            if successor is not None and (
                    (self.id < successor.id < id) or
                    (self.id > successor.id and successor.id < id) or
                    (self.id < successor.id and successor.id > id)):
                return successor
        return self

    def join(self, known_ip=None, known_port=None):
        if known_ip and known_port:
            print(f"Node {self.id} trying to join the network via node at {known_ip}:{known_port}")
            with grpc.insecure_channel(f'{known_ip}:{known_port}') as channel:
                stub = pb2_grpc.FileServiceStub(channel)
                response = stub.FindSuccessor(pb2.FindSuccessorRequest(id=self.id))
                self.successor = ChordNode(response.ip, response.port, m=self.m)
                self.predecessor = self
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
                self.update_successor(i, self)

    def stabilize(self):
        if self.successor:
            try:
                with grpc.insecure_channel(f'{self.successor.ip}:{self.successor.port}') as channel:
                    stub = pb2_grpc.FileServiceStub(channel)
                    response = stub.GetPredecessor(pb2.Empty())
                    if response.id:
                        x = ChordNode(response.ip, response.port, m=self.m)
                        if ((self.id < x.id < self.successor.id) or
                            (self.id >= self.successor.id and (x.id > self.id or x.id < self.successor.id))):
                            self.successor = x
                    stub.Notify(pb2.NotifyRequest(ip=self.ip, port=self.port, id=self.id))
            except grpc.RpcError as e:
                print(f"Stabilization failed with error: {e}")
        else:
            print(f"No successor found for Node {self.id}. Retrying stabilization.")

    def notify(self, node):
        if not self.predecessor or (
            (self.predecessor.id <= self.id and self.predecessor.id < node.id < self.id) or 
            (self.predecessor.id >= self.id and (node.id > self.predecessor.id or node.id < self.id))
        ):
            #print(f"Node {self.id} updated its predecessor to Node {node.id}")
            self.predecessor = node

 
    def fix_fingers(self):
        for i in range(self.m):
            start = (self.id + 2 ** i) % (2 ** self.m)
            successor = self.find_successor(start)
            self.finger_table[i]['start'] = start
            self.finger_table[i]['interval'] = (start, (start + 2 ** i) % (2 ** self.m))
            self.finger_table[i]['successor'] = successor
            
    def leave_network(self):
        with grpc.insecure_channel(f'{self.successor.ip}:{self.successor.port}') as channel:
            stub = pb2_grpc.FileServiceStub(channel)
            try:
                stub.UpdateFingerTable(pb2.fingerTable(node_leave_id=self.id, ip=self.successor.ip, port=self.successor.port))
            except grpc.RpcError as e:
                print(f"Failed update FT: {e}")
        
        if self.successor:
            successor = self.successor
            with grpc.insecure_channel(f'{successor.ip}:{successor.port}') as channel:
                stub = pb2_grpc.FileServiceStub(channel)
                stub.UpdatePredecessor(pb2.node(ip=self.predecessor.ip, port=self.predecessor.port))
            
        if self.predecessor:
            predecessor = self.predecessor
            with grpc.insecure_channel(f'{predecessor.ip}:{predecessor.port}') as channel:
                stub = pb2_grpc.FileServiceStub(channel)
                stub.UpdateSucesor(pb2.node(ip=self.successor.ip, port=self.successor.port))


    def update_finger_table(self, node_leave_id, successor_ip, successor_port):
        try:
            for index in range(self.m):
                if self.finger_table[index]['successor'].id == node_leave_id:
                    self.finger_table[index]['successor'] = ChordNode(successor_ip, successor_port, m=self.m)

            if self.successor.id != node_leave_id:
                with grpc.insecure_channel(f'{self.successor.ip}:{self.successor.port}') as channel:
                    stub = pb2_grpc.FileServiceStub(channel)
                    try:
                        stub.UpdateFingerTable(pb2.fingerTable(node_leave_id=node_leave_id, ip=successor_ip, port=successor_port))
                    except grpc.RpcError as e:
                        print(f"Failed to update finger table: {e}")
        except Exception as e:
            print(f"Error updating finger table: {e}")

    def update_predecessor(self, node):
        self.predecessor = node
        
    def update_sucesor(self, node):
        self.successor = node

    def start_server(self):
        global server
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        pb2_grpc.add_FileServiceServicer_to_server(FileService(self), server)
        
        health_servicer = health.HealthServicer()
        # health check service - add this service to server
        health_pb2_grpc.add_HealthServicer_to_server(health.HealthServicer(), server)
        
        # Setear el estado de salud inicial a "SERVING"
        health_servicer.set('', health_pb2.HealthCheckResponse.SERVING)
        
        server.add_insecure_port(f"{self.ip}:{self.port}")
        server.start()
        try:
            while True:
                self.stabilize()
                self.fix_fingers()
                time.sleep(5)
        except KeyboardInterrupt:
            server.stop(0)
            
    def stop_server(self):
        global server
        server.stop(grace=10)  # Espera hasta 5 segundos para completar las solicitudes activas
        print(f"Servidor gRPC detenido en {self.ip}:{self.port}")


#--------------------------------------------------------------

    def print_predecessor(self):
        if self.predecessor:
            print(f"\nPredecessor for node {self.id}: Node ID {self.predecessor.id}, Address: {self.predecessor.ip}:{self.predecessor.port}")
        else:
            print(f"\nPredecessor for node {self.id}: None")
    
    def print_successor(self):
        if self.successor:
            print(f"\nSuccessor for node {self.id}: Node ID {self.successor.id}, Address: {self.successor.ip}:{self.successor.port}")
        else:
            print(f"\nSuccessor for node {self.id}: None")
            
    def print_finger_table(self):
        print(f"Finger table for node {self.id}:")
        for i, entry in enumerate(self.finger_table):
            if entry:
                print(f"Entry {i}: Node ID {entry.id}, Address: {entry.ip}:{entry.port}")
            else:
                print(f"Entry {i}: None")
            
    def print_finger_table2(self):
        print(f"\nFinger table for node {self.id}:")
        print(tabulate([[entry['start'], entry['interval'], entry['successor'].id if entry['successor'] else None] for entry in self.finger_table], headers=['Start', 'Interval', 'Successor']))


    def update_successor(self, index, successor):
        self.finger_table[index]['successor'] = successor

    def get_successor(self, key):
        for entry in self.table:
            if entry['interval'][0] <= key < entry['interval'][1]:
                return entry['successor']
        return None
    
    def health_check(self):
        with grpc.insecure_channel(f"{self.ip}:{self.port}") as channel:
            stub = health_pb2_grpc.HealthStub(channel)
            response = stub.Check(health_pb2.HealthCheckRequest(service=''))
            print(response.status) 