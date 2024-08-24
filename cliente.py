import grpc
from services.fileservice_pb2_grpc import FileServiceStub
from services.fileservice_pb2 import FindSuccessorRequest

def test_connection(ip, port, target_id):
    # Crear un canal gRPC hacia el nodo destino
    with grpc.insecure_channel(f'{ip}:{port}') as channel:
        stub = FileServiceStub(channel)
        try:
            # Realizar una solicitud para encontrar el sucesor de target_id
            response = stub.FindSuccessor(FindSuccessorRequest(id=target_id))
            print(f"Success: Connected to {ip}:{port} and received successor {response.id}")
        except grpc.RpcError as e:
            print(f"Failed to connect to {ip}:{port}. Error: {e}")

if __name__ == "__main__":
    # Aquí especificas la IP y puerto del nodo al que quieres conectar
    # Por ejemplo, conectar desde el nodo 15 (localhost:50052) al nodo 21 (localhost:50051)
    test_connection("127.0.0.1", 50051, 21)
