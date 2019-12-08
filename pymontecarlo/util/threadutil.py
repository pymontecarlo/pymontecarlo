""""""

# Standard library modules.
import threading
import time
import atexit

# Third party modules.

# Local modules.

# Globals and constants variables.


class RepeatTimer(threading.Thread):
    """
    Call a function repeatedly after a specified number of seconds:

            t = Timer(30.0, f, args=None, kwargs=None)
            t.start()
            t.cancel()     # stop the timer's action if it's still waiting

    """

    def __init__(self, interval, function, args=None, kwargs=None):
        super().__init__()
        self.interval = interval
        self.function = function
        self.args = args if args is not None else []
        self.kwargs = kwargs if kwargs is not None else {}
        self.finished = threading.Event()

    def cancel(self):
        """Stop the timer."""
        self.finished.set()

    def run(self):
        while not self.finished.is_set():
            self.finished.wait(self.interval)

            if not self.finished.is_set():
                self.function(*self.args, **self.kwargs)
