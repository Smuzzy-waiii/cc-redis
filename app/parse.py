import sys

def parse_raw_data(raw_data: bytes):
    if not raw_data:
        return None, None

    data = raw_data.decode()
    data_arr = data.split("\r\n")

    prefix = data_arr[0]
    if prefix[0]!="*":
        sys.exit("Non Array Requests not supported")
    count = int(prefix[1:])

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