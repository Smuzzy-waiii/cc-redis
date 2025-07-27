import time

from app.datatypes.StreamID import StreamID
from app.datatypes.Item import Item
from app.datatypes.StreamEntry import StreamEntry

class Stream(Item):
    def __init__(self):
        super().__init__([], "stream")

    def add_entry(self, id, kvs):
        #validate entry id
        parts = id.split("-")
        milliseconds_time = int(parts[0]) if parts[0].isnumeric() else parts[0]
        seq_num = int(parts[1]) if parts[1].isnumeric() else parts[1]

        last_id = self.value[-1].id if len(self.value) > 0 else None

        if milliseconds_time == '*':
            # set milliseconds_time to current unix time in ms
            milliseconds_time = int(time.time()*1000)

        if seq_num == '*':
            if last_id and last_id.milliseconds_time==milliseconds_time:
                seq_num = last_id.seq_num + 1
            elif milliseconds_time == 0:
                seq_num = 1
            else:
                seq_num = 0

        id_to_add = StreamID(milliseconds_time, seq_num)
        if not (id_to_add > StreamID(0, 0)):
            raise StreamIDNotGreaterThanZero()
        if last_id and not (id_to_add > last_id):
            raise StreamIDNotGreaterThanLastID()

        entry = StreamEntry(id_to_add, kvs)
        self.value.append(entry)
        return entry

    def xrange(self, start: StreamID, end: StreamID):
        result = []
        for entry in self.value:
            if entry.id <= end and entry.id >= start:
                data = []
                for k, v in entry.data.items():
                    data.extend([k, v])
                result.append([str(entry.id), data])
        return result

class StreamIDNotGreaterThanLastID(Exception):
    pass

class StreamIDNotGreaterThanZero(Exception):
    pass