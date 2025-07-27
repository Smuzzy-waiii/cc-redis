from app.datatypes.Item import Item
from app.datatypes.StreamEntry import StreamEntry


class Stream(Item):
    def __init__(self):
        super().__init__([], "stream")

    def add_entry(self, id, kvs):
        self.value.append(StreamEntry(id, kvs))