import asyncio

from app.grpc.book_grpc_client import BookGrpcClient


async def main():
    client = BookGrpcClient()

    book = await client.get_book(1)
    print(book)

    reservation = await client.reserve_book(1)
    print(reservation)


if __name__ == "__main__":
    asyncio.run(main())
