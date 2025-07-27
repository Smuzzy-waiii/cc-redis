import time

from app.datatypes.StreamID import StreamID
from app.datatypes.Item import Item
from app.datatypes.StreamEntry import StreamEntry

class Stream(Item):
    def __init__(self):
        super().__init__([], "stream")

    def add_entry(self, id, kvs):
        #validate entry id
        id_to_add = StreamID.from_string(id)
        last_id = self.value[-1].id if len(self.value) > 0 else None

        if id_to_add.milliseconds_time == -1:
            # set milliseconds_time to current unix time in ms
            id_to_add.milliseconds_time = int(time.time()*1000)

        if id_to_add.seq_num == -1: #seq_num=*
            if last_id and last_id.milliseconds_time==id_to_add.milliseconds_time:
                id_to_add.seq_num = last_id.seq_num + 1
            elif id_to_add.milliseconds_time == 0:
                id_to_add.seq_num = 1
            else:
                id_to_add.seq_num = 0

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