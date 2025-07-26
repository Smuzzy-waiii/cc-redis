DEV_MODE = False

def devprint(*args):
    if DEV_MODE:
        print(*args)

def resp_format_data_raw(val, datatype) -> str :
    if datatype == 'int':
        return f":{val}\r\n"
    elif datatype == "simplestr":
        return f"+{val}\r\n"
    elif datatype == 'bulkstr':
        if val is None:
            return "$-1\r\n"
        return f"${len(val)}\r\n{val}\r\n"
    elif datatype == 'array':
        res = f"*{len(val)}\r\n"
        for v in val:
            res += resp_format_data_raw(v, "bulkstr")
        return res
    else:
        raise Exception(f"Unsupported datatype: {datatype}")

def resp_format_data(val, datatype) -> bytes:
    return resp_format_data_raw(val, datatype).encode()