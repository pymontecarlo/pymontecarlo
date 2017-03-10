""""""

# Standard library modules.
import concurrent.futures

# Third party modules.

# Local modules.
from pymontecarlo.util.cbook import Monitorable

# Globals and constants variables.

class Token:

    def __init__(self):
        self._progress = 0.0
        self._status = ''
        self._cancelled = False

    def cancel(self):
        self._cancelled = True

    def cancelled(self):
        return self._cancelled

    def update(self, progress, status):
        self._progress = progress
        self._status = status

    @property
    def progress(self):
        return self._progress

    @property
    def status(self):
        return self._status

class FutureAdapter(Monitorable):

    def __init__(self, future, token):
        self.future = future
        self.token = token

    def running(self):
        return self.future.running()

    def cancelled(self):
        # NOTE: future cancel always returns False
        return self.token.cancelled()

    def cancel(self):
        # NOTE: future cancel always returns False
        self.token.cancel()

    def done(self):
        return self.future.done()

    def result(self, timeout=None):
        return self.future.result(timeout)

    def exception(self, timeout=None):
        return self.future.exception(timeout)

    def add_done_callback(self, fn):
        return self.future.add_done_callback(lambda f: fn(self))

    def wait(self, timeout=None):
        self.result(timeout)

    @property
    def progress(self):
        return self.token.progress

    @property
    def status(self):
        return self.token.status

class FutureExecutor(Monitorable):

    def __init__(self, max_workers=1):
        self.max_workers = max_workers
        self.executor = None

        self.failed_count = 0
        self.cancelled_count = 0
        self.submitted_count = 0
        self.done_count = 0

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exctype, value, tb):
        self.shutdown(wait=True)
        return False

    def _on_done(self, future):
        if future.cancelled():
            self.cancelled_count += 1
            return

        if future.exception():
            self.failed_count += 1
            return

        self.done_count += 1
        return future.result()

    def start(self):
        if self.executor is not None:
            raise RuntimeError('Already started')
        self.executor = concurrent.futures.ThreadPoolExecutor(self.max_workers)

    def shutdown(self, wait=True):
        if self.executor is None:
            return
        self.executor.shutdown(wait)
        self.executor = None

    def wait(self, timeout=None):
        _done, notdone = \
            concurrent.futures.wait(self.futures, timeout, concurrent.futures.ALL_COMPLETED)
        return not notdone

    def submit(self, target, *args, **kwargs):
        token = Token()
        future = self.executor.submit(target, token, *args, **kwargs)

        future = FutureAdapter(future, token)
        future.add_done_callback(self._on_done)
        self.submitted_count += 1

        return future

    def running(self):
        return self.executor is not None

    def cancelled(self):
        return False

    @property
    def progress(self):
        return (self.done_count + self.failed_count + self.cancelled_count) / self.submitted_count

    @property
    def status(self):
        return ''

