import asyncio
import os
import socket  # noqa: F401

from app.helpers import devprint, DEV_MODE
from app.parse import parse_raw_data
from app.process import process

async def handle_client(reader, writer):
    devprint("Client connected")

    while True:
        raw_data = await reader.read(1024)
        vals, count = parse_raw_data(raw_data)

        if vals is None:
            await writer.drain()
            writer.close()
            await writer.wait_closed()
            return
        else:
            devprint("vals: ", vals)
            process(vals, writer)


async def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    if os.getenv("DEV_MODE"):
        global DEV_MODE
        DEV_MODE = True
        print("Running in development mode")

    server = await asyncio.start_server(
        handle_client, 'localhost', 6379, reuse_port=True
    )
    addr = server.sockets[0].getsockname()
    print(f'Serving on {addr}')

    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())