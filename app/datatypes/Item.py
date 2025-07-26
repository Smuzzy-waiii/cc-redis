class Item:
    def __init__(self, value, type):
        self.value = value
        self.type = type

    def to_dict(self):
        return {
            'value': self.value,
            'type': self.type
        }

    def from_dict(self, data):
        self.value = data['value']
        self.type = data['type']