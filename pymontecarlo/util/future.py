""""""

# Standard library modules.
import concurrent.futures

# Third party modules.

# Local modules.
from pymontecarlo.util.cbook import Monitorable
from pymontecarlo.util.signal import Signal

# Globals and constants variables.

class Token:

    def __init__(self):
        self._progress = 0.0
        self._status = 'Not started'
        self._cancelled = False

    def cancel(self):
        self._cancelled = True
        self.update(1.0, 'Cancelled')

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

    def __init__(self, future, token, args, kwargs):
        self.future = future
        self.token = token
        self.args = args
        self.kwargs = kwargs

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

    submitted = Signal()

    def __init__(self, max_workers=1):
        self.max_workers = max_workers
        self.executor = None
        self.futures = set()
        self.failed_futures = set()

        self.failed_count = 0
        self.cancelled_count = 0
        self.submitted_count = 0
        self.done_count = 0

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exctype, value, tb):
        self.shutdown()
        return False

    def _on_done(self, future):
        if future.cancelled():
            future.token.update(1.0, 'Cancelled')
            self.cancelled_count += 1
            return

        if future.exception():
            future.token.update(1.0, 'Error')
            self.failed_futures.add(future)
            self.failed_count += 1
            return

        future.token.update(1.0, 'Done')
        self.done_count += 1
        return future.result()

    def start(self):
        if self.executor is not None:
            return
        self.executor = concurrent.futures.ThreadPoolExecutor(self.max_workers)

    def cancel(self):
        """
        Cancels all not completed futures.
        """
        for future in self.futures:
            if not future.done():
                future.cancel()

    def shutdown(self):
        if self.executor is None:
            return
        self.executor.shutdown(wait=True)
        self.futures.clear()

    def wait(self, timeout=None):
        """
        Waits forever if *timeout* is ``None``. 
        Otherwise waits for *timeout* and returns ``True`` if all submissions
        were executed, ``False`` otherwise.
        """
        fs = [future.future for future in self.futures]
        _done, notdone = \
            concurrent.futures.wait(fs, timeout, concurrent.futures.ALL_COMPLETED)
        return not notdone

    def _submit(self, target, *args, **kwargs):
        """
        Submits target function with specified arguments.
        
        .. note:: The derived class should ideally create a :meth:`submit` 
            method that calls this method.
        
        :arg target: function to execute. The first argument of the function
            should be a token, where the progress, status of the function
            can be updated::
            
            def target(token):
                token.update(0.0, 'start')
                if token.cancelled():
                    return
                token.update(1.0, 'done')
        
        :return: a :class:`Future` object
        """
        if self.executor is None:
            raise RuntimeError('Executor is not started')

        token = Token()
        future = self.executor.submit(target, token, *args, **kwargs)

        future2 = FutureAdapter(future, token, args, kwargs)
        future2.add_done_callback(self._on_done)
        self.futures.add(future2)

        self.submitted_count += 1
        self.submitted.send(future2)

        return future2

    def running(self):
        """
        Returns whether the executor is running and can accept submission.
        """
        return any(future.running() for future in self.futures)

    def done(self):
        return all(future.done() for future in self.futures)

    def cancelled(self):
        return False

    @property
    def progress(self):
        if self.submitted_count == 0:
            return 0
        return (self.done_count + self.failed_count + self.cancelled_count) / self.submitted_count

    @property
    def status(self):
        return ''
