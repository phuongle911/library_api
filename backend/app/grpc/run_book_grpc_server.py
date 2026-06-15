import asyncio

from app.grpc.book_grpc_server import BookService

if __name__ == "__main__":
    asyncio.run(BookService.serve())
