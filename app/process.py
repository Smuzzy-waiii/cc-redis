import time
from datetime import datetime, timedelta

from app.datatypes.Item import Item
from app.datatypes.KeyVal import KeyVal
from app.datatypes.List import RedisList
from app.datatypes.Stream import Stream, StreamIDNotGreaterThanZero, StreamIDNotGreaterThanLastID
from app.datatypes.StreamID import StreamID
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

    elif _command=="TYPE":
        key = vals[1]
        val = KV_CACHE.get(key, Item(None, "none"))
        writer.write(resp_format_data(val.get_type(), "simplestr"))

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
        length = len(existing_list)
        writer.write(resp_format_data(length, "int"))

    # LPOP <LIST_KEY> => popped elem
    elif _command == "LPOP":
        key = vals[1]
        amt_to_pop = 1

        if len(vals) > 2:
            amt_to_pop = int(vals[2])

        existing_list = KV_CACHE.get(key, RedisList())
        popped = existing_list.lpop(amt_to_pop)
        KV_CACHE[key] = existing_list

        resp_type = "array" if popped and amt_to_pop > 1 else "bulkstr"
        writer.write(resp_format_data(popped, resp_type))

    elif _command == "BLPOP":
        key = vals[1]
        exp = float(vals[2])

        existing_list = KV_CACHE.get(key, RedisList())
        popped = existing_list.lpop(1)
        if popped:
            KV_CACHE[key] = existing_list
            writer.write(resp_format_data([key, popped], "array"))
            return

        id = existing_list.stand_in_queue()
        exp_time = time.monotonic()+exp if exp!=0 else None
        KV_CACHE[key] = existing_list
        while True:
            existing_list = KV_CACHE[key]
            if not existing_list.still_in_queue(id):
                writer.write(resp_format_data(None, "bulkstr"))
                return

            if exp_time and time.monotonic()>exp_time:
                existing_list.exit_queue(id)
                writer.write(resp_format_data(None, "bulkstr"))
                return

            can_be_popped = len(existing_list)>0
            if can_be_popped:
                if existing_list.top_of_queue(id):
                    popped = existing_list.lpop(1)
                    KV_CACHE[key] = existing_list
                    writer.write(resp_format_data([key, popped], "array"))
                return

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

    elif _command=="XADD":
        key = vals[1]
        entry_id = vals[2]
        kvs = {}
        i = 3
        while i < len(vals):
            kvs[vals[i]] = vals[i+1]
            i+=2

        if entry_id == "*":
            entry_id = "*-*"
        stream = KV_CACHE.get(key, Stream())

        try:
            entry = stream.add_entry(entry_id, kvs)
        except StreamIDNotGreaterThanLastID:
            writer.write(resp_format_data("ERR The ID specified in XADD is equal or smaller than the target stream top item", "simpleerror"))
            return
        except StreamIDNotGreaterThanZero:
            writer.write(resp_format_data("ERR The ID specified in XADD must be greater than 0-0", "simpleerror"))
            return

        KV_CACHE[key] = stream
        writer.write(resp_format_data(str(entry.id), "bulkstr"))

    elif _command == "XRANGE":
        key = vals[1]
        startstr= vals[2]
        endstr = vals[3]

        if "-" not in startstr:
            startstr=startstr+"-0"
        if "-" not in endstr:
            endstr=endstr+"-99999999999999999999"
        start = StreamID.from_string(startstr)
        end = StreamID.from_string(endstr)

        stream = KV_CACHE.get(key, Stream())
        res = stream.xrange(start, end)
        writer.write(resp_format_data(res, "array"))

    else:
        writer.write(resp_format_data(f"Invalid command: {_command}", "bulkstr"))
