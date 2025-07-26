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

def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    # Uncomment this to pass the first stage

    #
    server_socket = socket.create_server(("localhost", 6379), reuse_port=True)
    conn, _ = server_socket.accept() # wait for client
    while True:
        raw_data = conn.recv(1024)
        vals, count = process_raw_data(raw_data)
        if vals is not None:
            print("vals: ", vals)
            for val in vals:
                if val == "PING":
                    conn.sendall(b"+PONG\r\n")

if __name__ == "__main__":
    main()
