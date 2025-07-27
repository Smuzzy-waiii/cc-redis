class StreamID:
    def __init__(self, milliseconds_time, seq_num):
        self.milliseconds_time = milliseconds_time
        self.seq_num = seq_num

    def from_string(string):
        milliseconds_time, seq_num = string.split('-')
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