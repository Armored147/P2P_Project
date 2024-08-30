from concurrent import futures
import grpc
from services import fileservice_pb2_grpc as pb2_grpc
from . import fileservice_pb2 as pb2
from . import chordNode
import time

class FileService(pb2_grpc.FileServiceServicer):
    def __init__(self, chord_node):
        self.chord_node = chord_node

    
    def DownloadFile(self, request, context):
        filename = request.filename
        if str(filename) in self.chord_node.file_list:  # Comparar como cadena
            return pb2.FileResponse(message=f"{filename}")  # Mensaje de éxito
        else:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f'Archivo {filename} no encontrado en el nodo {self.chord_node.id}')
            return pb2.FileResponse(message="")  # Mensaje de archivo no encontrado


    def FindSuccessor(self, request, context):
        successor = self.chord_node.find_successor(request.id)
        return pb2.FindSuccessorResponse(ip=successor.ip, port=successor.port, id=successor.id)
    
    def Notify(self, request, context):
        node = chordNode.ChordNode(request.ip, request.port, self.chord_node.m)
        self.chord_node.notify(node)
        return pb2.Empty()
    
    def GetPredecessor(self, request, context):
        predecessor = self.chord_node.predecessor
        if predecessor:
            return pb2.GetPredecessorResponse(ip=predecessor.ip, port=predecessor.port, id=predecessor.id)
        return pb2.GetPredecessorResponse(ip="", port=0, id=0)
    
    def UpdatePredecessor(self, request, context):
        self.chord_node.update_predecessor(chordNode.ChordNode(request.ip, request.port, self.chord_node.m))
        return pb2.Empty()

    def UpdateSucesor(self, request, context):
        self.chord_node.update_sucesor(chordNode.ChordNode(request.ip, request.port, self.chord_node.m))
        return pb2.Empty()

    def UpdateFingerTable(self, request, context):
        self.chord_node.update_finger_table(request.node_leave_id, request.ip, request.port)
        return pb2.Empty()


#--------------------------------------------------------------

def serve(config, chord_node):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pb2_grpc.add_FileServiceServicer_to_server(FileService(chord_node), server)
    server.add_insecure_port(f"{config['ip']}:{config['port']}")
    server.start()
    print(f"Server started on {config['ip']}:{config['port']}")
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)
