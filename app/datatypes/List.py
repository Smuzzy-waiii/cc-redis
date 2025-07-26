import random

from app.datatypes.Item import Item

class RedisList(Item):
    def __init__(self, value=[]):
        super().__init__(value, "list")
        self.blocking_queue = []

    def __len__(self):
        return len(self.value)

    def stand_in_queue(self):
        id = random.randint(0, 1_000_000)
        self.blocking_queue.append(id)
        return id

    def top_of_queue(self, id):
        return self.blocking_queue[0] == id

    def exit_queue(self, id):
        self.blocking_queue.remove(id)

    def clear_queue(self):
        self.blocking_queue = []

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
        return popped if amt_to_pop > 1 else popped[0]

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