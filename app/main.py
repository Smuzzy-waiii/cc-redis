import asyncio
import socket  # noqa: F401
import sys
from datetime import datetime, timedelta
from shutil import Error

from future.backports.datetime import datetime

KV_CACHE = {}

def resp_format_data(val, datatype) -> bytes :
    if datatype == 'int':
        return f":{val}\r\n".encode()
    elif datatype == "simplestr":
        return f"+{val}\r\n".encode()
    elif datatype == 'bulkstr':
        if val is None:
            return "$-1\r\n".encode()
        return f"${len(val)}\r\n{val}\r\n".encode()
    else:
        raise Error(f"Unsupported datatype: {datatype}")

def parse_raw_data(raw_data: bytes):
    if not raw_data:
        return None, None

    data = raw_data.decode()
    data_arr = data.split("\r\n")

    prefix = data_arr[0]
    if prefix[0]!="*":
        sys.exit("Non Array Requests not supported")
    count = int(prefix[1])

    vals = []
    idx = 0
    for i in range(count):
        idx+=1
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

def process(vals, writer):
    _command = vals[0].upper()
    if _command=="PING":
        writer.write(resp_format_data( "PONG", "simplestr"))
    elif _command=="ECHO":
        resp = resp_format_data(vals[1], "bulkstr")
        writer.write(resp)


    elif _command=="SET":
        key = vals[1]
        value = vals[2]

        # opts = {}
        # #check for expiry
        # if len(vals) > 3:
        #     i=3
        #     while i < len(vals):
        #         elem = vals[i]
        #         if elem == "px":
        #             i+=1
        #             opts["px"] = vals[i]
        #         i+=1

        expiry = None
        if len(vals) > 3 and vals[3].lower() =="px":
            expiry = int(vals[4])

        KV_CACHE[key] = {
            "value": value,
            "exp": datetime.now() + timedelta(milliseconds=expiry) if expiry else None,
        }
        writer.write(resp_format_data("OK", "simplestr"))


    elif _command=="GET":
        key = vals[1]
        valueset = KV_CACHE.get(key)
        value = None

        if valueset:
            exp = valueset.get("exp")
            if not exp or exp >= datetime.now(): #TODO: remove KV from cache if expired to save memory
                value = valueset.get("value")

        writer.write(resp_format_data(value, "bulkstr"))

    else:
        writer.write(resp_format_data(f"Invalid command: {_command}", "bulkstr"))

async def handle_client(reader, writer):
    print("Client connected")

    while True:
        raw_data = await reader.read(1024)
        vals, count = parse_raw_data(raw_data)

        if vals is None:
            await writer.drain()
            writer.close()
            await writer.wait_closed()
            return
        else:
            print("vals: ", vals)
            process(vals, writer)


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