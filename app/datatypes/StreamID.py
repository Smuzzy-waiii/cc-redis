class StreamID:
    def __init__(self, milliseconds_time, seq_num):
        self.milliseconds_time = int(milliseconds_time) if milliseconds_time.isnumeric() else -1
        self.seq_num = int(seq_num) if seq_num.isnumeric() else -1

    def from_string(s):
        milliseconds_time, seq_num = s.split('-')
        return StreamID(milliseconds_time, seq_num)

    def __str__(self):
        return f'{self.milliseconds_time}-{self.seq_num}'

    def __eq__(self, other):
        return self.milliseconds_time == other.milliseconds_time and self.seq_num == other.seq_num

    def __gt__(self, other):
        if self.milliseconds_time > other.milliseconds_time:
            return True
        if self.milliseconds_time == other.milliseconds_time:
            return self.seq_num > other.seq_num
        return False

    def __lt__(self, other):
        if self.milliseconds_time < other.milliseconds_time:
            return True
        if self.milliseconds_time == other.milliseconds_time:
            return self.seq_num < other.seq_num
        return False

    def __ge__(self, other):
        return self > other or self == other

    def __le__(self, other):
        return self < other or self == other