from app.datatypes.Item import Item

class RedisList(Item):
    def __init__(self, value=[]):
        super().__init__(value, "list")
        self.blocking_queue = []

    def __len__(self):
        return len(self.value)

    def rpush(self, values):
        self.value.extend(values)

    def lpush(self, values):
        self.value = values[::-1] + self.value

    def lpop(self, amt_to_pop):
        if len(self.value) == 0:
            return None

        amt_to_pop = min(amt_to_pop, len(self.value))
        popped = self.value[:amt_to_pop]
        self.value = self.value[amt_to_pop:]
        return popped

    def lrange(self, start_idx, end_idx):
        values = self.value
        if end_idx < 0:
            end_idx = len(values)+end_idx
        if start_idx < 0:
            start_idx = len(values)+start_idx

        if values == []:
            retval = []
        elif start_idx >= len(values):
            retval = []
        elif start_idx > end_idx:
            retval = []
        else:
            if start_idx < 0:
                start_idx = 0
            if end_idx >= len(values):
                end_idx = len(values)-1
            retval = values[start_idx:end_idx+1]
        return retval

    def from_dict(self, d):
        super().from_dict(d)
        self.blocking_queue = d["blocking_queue"]

    def to_dict(self):
        retval = super().to_dict()
        retval["blocking_queue"] = self.blocking_queue