import datetime
from typing import Optional

class HistoryItem:
    def __init__(self, item, timestamp=datetime.datetime.now()):
        self.item = item
        self.timestamp = timestamp

    def __repr__(self):
        return f'[{self.timestamp}]: {self.item}'

    def __str__(self):
        return f'[{self.timestamp}]: {self.item}'

    def __lt__(self, other):
        if type(other) is datetime.datetime:
            return self.timestamp < other
        return self < other.timestamp

    def __gt__(self, other):
        return not (self <= other)

    def __le__(self, other):
        return self.timestamp <= other.timestamp

class History:
    def __init__(self, capacity=400):
        self.capacity = capacity
        self._history = list()

    def __getitem__(self, before):
        return filter(lambda x: x < before, self._history)

    def __contains__(self, item):
        return self.lookup(item) is not None

    def __sizeof__(self):
        return len(self._history)

    def add(self, item, timestamp=datetime.datetime.now()):
        self._history.append(HistoryItem(item=item, timestamp=timestamp))
        if len(self._history) > self.capacity:
            self._history.pop(0)

    def lookup(self, item, before: Optional[datetime.datetime] = None):
        def _lookup(items):
            for h in items:
                if h.item == item:
                    return h
            return None

        if before is not None:
            return _lookup(self[before])
        return _lookup(self._history)


