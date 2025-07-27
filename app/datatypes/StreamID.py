class StreamID:
    # CONVENTION
    # milliseconds_time: START=0, END=-1
    # seq_num: START=0/1, END=-1
    def __init__(self, milliseconds_time, seq_num):
        self.milliseconds_time = int(milliseconds_time)
        self.seq_num = int(seq_num)

    @staticmethod
    def from_string(sid, default_max=False):
        if sid == "-":
            return StreamID(0, 0)

        if sid == "+":
            return StreamID(-1, -1)

        if "-" not in sid:
            return StreamID(sid, -1) if default_max else StreamID(sid, 0)

        milliseconds_time, seq_num = sid.split('-')
        return StreamID(milliseconds_time, seq_num)

    def __str__(self):
        return f'{self.milliseconds_time}-{self.seq_num}'

    def __eq__(self, other):
        return self.milliseconds_time == other.milliseconds_time and self.seq_num == other.seq_num

    def __gt__(self, other):
        if self.milliseconds_time == other.milliseconds_time:
            if self.seq_num == other.seq_num:
                return False
            if self.seq_num == -1:
                return True
            if other.seq_num == -1:
                return False
            return self.milliseconds_time > other.milliseconds_time

        if self.milliseconds_time == -1:
            return True
        if other.milliseconds_time == -1:
            return False

        return self.milliseconds_time > other.milliseconds_time

    def __lt__(self, other):
        return not self >= other

    def __ge__(self, other):
        return self > other or self == other

    def __le__(self, other):
        return self < other or self == other