from datetime import datetime


class TimeCalculator:
    def __init__(self):
        self._start = None
        self._end = None

    def start(self):
        self._start = datetime.now()

    def end(self):
        self._end = datetime.now()

    def delta(self):
        delta = self._end - self._start
        print(delta)
