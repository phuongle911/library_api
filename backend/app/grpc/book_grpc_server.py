import grpc
from grpc import aio

from app.grpc import book_service_pb2 as book__service__pb2
from app.grpc import book_service_pb2_grpc


class BookService(book_service_pb2_grpc.BookServiceServicer):
    async def GetBook(self, request, context):
        return book__service__pb2.BookResponse(
            id=request.book_id,
            title=f"book_{request.book_id}",
            available_copies=5,
        )
    
    async def ReserveBook(self, request, context):
        return book__service__pb2.ReserveBookResponse(
            success=True,
            message="Book reserved successfully",
        )
    
    async def serve():
        server = aio.server()
        book_service_pb2_grpc.add_BookServiceServicer_to_server(
            BookService(),
            server,
        )

        server.add_insecure_port("[::]:50051")
        await server.start()
        print("Book gRBC server running on port 50051")

        await server.wait_for_termination()
