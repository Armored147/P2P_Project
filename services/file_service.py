from concurrent import futures
import grpc
from services import fileservice_pb2_grpc as pb2_grpc
from services import fileservice_pb2 as pb2
import time

class FileService(pb2_grpc.FileServiceServicer):
    def __init__(self, chord_node):
        self.chord_node = chord_node
    
    def UploadFile(self, request, context):
        # Implementación DUMMY
        return pb2.FileResponse(message=f"Received file: {request.filename}")
    
    def DownloadFile(self, request, context):
        # Implementación DUMMY
        return pb2.FileResponse(message=f"Sending file: {request.filename}")

    def FindSuccessor(self, request, context):
        successor = self.chord_node.find_successor(request.id)
        return pb2.FindSuccessorResponse(ip=successor.ip, port=successor.port, id=successor.id)

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
