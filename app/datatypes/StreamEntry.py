from app.datatypes.StreamID import StreamID


class StreamEntry:
    def __init__(self, id, kvs=None):
        self.id = id
        self.data = {} if kvs is None else kvs

    def addkv(self , key, value):
        self.data[key] = value