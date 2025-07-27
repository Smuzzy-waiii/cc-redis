from app.datatypes.StreamID import StreamID
from app.datatypes.Item import Item
from app.datatypes.StreamEntry import StreamEntry

class Stream(Item):
    def __init__(self):
        super().__init__([], "stream")

    def add_entry(self, id, kvs):
        #validate entry id
        id_to_add = StreamID.from_string(id)
        if not (id_to_add > StreamID("0", "0")):
            raise StreamIDNotGreaterThanZero()

        last_id = self.value[-1].id if len(self.value) > 0 else None
        if last_id and not (id_to_add > last_id):
            raise StreamIDNotGreaterThanLastID()

        self.value.append(StreamEntry(id_to_add, kvs))

class StreamIDNotGreaterThanLastID(Exception):
    pass

class StreamIDNotGreaterThanZero(Exception):
    pass