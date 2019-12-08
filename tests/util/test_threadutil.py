""""""

# Standard library modules.
import time

# Third party modules.

# Local modules.
from pymontecarlo.util.threadutil import RepeatTimer

# Globals and constants variables.


class _Counter:
    def __init__(self):
        self.n = 0

    def increment(self):
        self.n += 1

    def get(self):
        return self.n


def test_repeattimer():
    counter = _Counter()
    timer = RepeatTimer(0.1, counter.increment)
    timer.start()

    time.sleep(0.5)
    timer.cancel()

    assert counter.get() >= 4
