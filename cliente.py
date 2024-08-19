import grpc
import services.fileservice_pb2_grpc as pb2_grpc
import services.fileservice_pb2 as pb2

def run():
    with grpc.insecure_channel('127.0.0.1:50051') as channel:
        stub = pb2_grpc.FileServiceStub(channel)
        response = stub.UploadFile(pb2.FileRequest(filename="example.txt"))
        print("Upload response: ", response.message)

        response = stub.DownloadFile(pb2.FileRequest(filename="example.txt"))
        print("Download response: ", response.message)

if __name__ == "__main__":
    run()
