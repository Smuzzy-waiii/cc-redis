import time
from app.datatypes.Item import Item

class KeyVal(Item):
    def __init__(self, value, expiry_time=None):
        super().__init__(value, "string")
        self.exp = time.monotonic() + expiry_time*0.001 if expiry_time else None

    def get_value(self):
        if self.exp and time.monotonic() > self.exp:
            return None
        else:
            return self.value

    def to_dict(self):
        retval = super().to_dict()
        retval['exp'] = self.exp
        return retval

    def from_dict(self, d):
        if d is None:
            d = {
                "value": None,
                "exp": None,
                "type": None
            }
        super().from_dict(d)
        self.exp = time.monotonic() + d['exp']*0.001 if 'exp' in d and d["exp"] else None