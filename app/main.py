import asyncio
import socket  # noqa: F401
import sys
from sys import prefix


def process_raw_data(raw_data: bytes):
    if not raw_data:
        return None, None

    data = raw_data.decode()
    data_arr = data.split("\r\n")

    prefix = data_arr[0]
    if prefix[0]!="*":
        sys.exit("Non Array Requests not supported")
    count = int(prefix[1])

    vals = []
    idx = 1
    for i in range(count):
        next_elem = data_arr[idx]

        control_char = next_elem[0]
        raw_val = next_elem[1:]

        val = None
        if control_char == "$": #bulk string eg: $5\r\nhello\r\n
            idx+=1
            val = data_arr[idx]
        elif control_char == ":": #integer eg: :5\r\n
            val = int(raw_val)
        elif control_char == "+": #simple string eg: +hello\r\n
            val = raw_val

        if val is not None:
            vals.append(val)
    return vals, count

async def handle_client(reader, writer):
    print("Client connected")

    while True:
        raw_data = await reader.read(1024)
        vals, count = process_raw_data(raw_data)

        if vals is None:
            await writer.drain()
            writer.close()
            await writer.wait_closed()
            return
        else:
            print("vals: ", vals)
            for val in vals:
                if val == "PING":
                    writer.write(b"+PONG\r\n")

async def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    server = await asyncio.start_server(
        handle_client, 'localhost', 6379, reuse_port=True
    )
    addr = server.sockets[0].getsockname()
    print(f'Serving on {addr}')

    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())