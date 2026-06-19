import grpc

from app.grpc import (
    book__service__pb2 as book_service_pb2, book_service_pb2_grpc,
)
from app.grpc import book_service_pb2
from app.grpc import book_service_pb2_grpc


class BookGrpcClient:
    def __init__(self, target: str = "localhost:50051"):
        self.target = target

    async def get_book(self, book_id: int):
        async with grpc.aio.insecure_channel(self.target) as channel:
            stub = book_service_pb2_grpc.BookServiceStub(channel)
            request = book_service_pb2.GetBookRequest(
                book_id=book_id
            )
            return await stub.GetBook(request)
        
    async def reserve_book(self, book_id: int):
        async with grpc.aio.insecure_channel(self.target) as channel:
            stub = book_service_pb2_grpc.BookServiceStub(channel)
            request = book_service_pb2.ReserveBookRequest(book_id=book_id)
            return await stub.ReserveBook(request)

    async def confirm_reservation(self, book_id: int):
        async with grpc.aio.insecure_channel(self.target) as channel:
            stub = book_service_pb2_grpc.BookServiceStub(channel)
            request = book_service_pb2.ConfirmReservationRequest(book_id=book_id)
            return await stub.ConfirmReservation(request)
        
    async def cancel_reservation(self, book_id: int):
        async with grpc.aio.insecure_channel(self.target) as channel:
            stub = book_service_pb2_grpc.BookServiceStub(channel)
            request = book_service_pb2.CancelReservationRequest(book_id=book_id)
            return await stub.CancelReservation(request)
