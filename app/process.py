from datetime import datetime, timedelta

from app.datatypes.KeyVal import KeyVal
from app.datatypes.List import RedisList
from app.helpers import resp_format_data

KV_CACHE = {}

def process(vals, writer):
    _command = vals[0].upper()
    if _command=="PING":
        writer.write(resp_format_data( "PONG", "simplestr"))

    # ECHO <str> => <str>
    elif _command=="ECHO":
        resp = resp_format_data(vals[1], "bulkstr")
        writer.write(resp)

    # SET <key> <value> PX <expiry: ms> => OK
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

        KV_CACHE[key] = KeyVal(value, expiry)
        writer.write(resp_format_data("OK", "simplestr"))

    # GET <key> => <value> or nil
    elif _command=="GET":
        key = vals[1]
        valueobj = KV_CACHE.get(key, KeyVal(None))
        value = valueobj.get_value()
        writer.write(resp_format_data(value, "bulkstr"))

    #RPUSH <LIST_KEY> <ITEM> => [..., <ITEM>]
    elif _command=="RPUSH":
        key = vals[1]
        values = vals[2:]

        existing_list = KV_CACHE.get(key, RedisList())
        existing_list.rpush(values)
        KV_CACHE[key] = existing_list
        writer.write(resp_format_data(len(existing_list), "int"))

    # LPUSH <LIST_KEY> <ITEM> => [<ITEM>, ...]
    elif _command == "LPUSH":
        key = vals[1]
        values = vals[2:]

        existing_list = KV_CACHE.get(key, RedisList())
        existing_list.lpush(values)
        KV_CACHE[key] = existing_list
        writer.write(resp_format_data(len(existing_list), "int"))

    # LLEN <LIST_KEY> => <length_of_list>
    elif _command == "LLEN":
        key = vals[1]
        existing_list = KV_CACHE.get(key, RedisList())
        writer.write(resp_format_data(len(existing_list), "int"))

    # LPOP <LIST_KEY> => popped elem
    elif _command == "LPOP":
        key = vals[1]
        amt_to_pop = 1

        if len(vals) > 2:
            amt_to_pop = int(vals[2])

        existing_list = KV_CACHE.get(key, RedisList())
        popped = existing_list.lpop(amt_to_pop)
        KV_CACHE[key] = existing_list

        retval = popped if amt_to_pop > 1 else popped[0]
        resp_type = "array" if popped and amt_to_pop > 1 else "bulkstr"
        writer.write(resp_format_data(retval, resp_type))

    #LRANGE <key> <start_idx> <end_idx>
    elif _command=="LRANGE":
        if len(vals) < 4:
            writer.write(resp_format_data("format: LRANGE <key> <start_idx> <end_idx>", "bulkstr"))
            return

        key = vals[1]
        start_idx = int(vals[2])
        end_idx = int(vals[3])

        existing_list = KV_CACHE.get(key, RedisList())
        retval = existing_list.lrange(start_idx, end_idx)
        writer.write(resp_format_data(retval, "array"))

    else:
        writer.write(resp_format_data(f"Invalid command: {_command}", "bulkstr"))
