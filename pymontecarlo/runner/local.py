"""
Local runner.
"""

# Standard library modules.
import concurrent.futures

# Third party modules.

# Local modules.
from pymontecarlo.runner.base import Runner, Tracker
from pymontecarlo.exceptions import WorkerCancelledError

# Globals and constants variables.

class LocalTracker(Tracker):

    def __init__(self, options, worker, future):
        super().__init__(options)
        self.worker = worker
        self.future = future

    def cancel(self):
        self.future.cancel()
        self.worker.cancel()

    @property
    def progress(self):
        return self.worker.progress

    @property
    def status(self):
        return self.worker.status

class LocalRunner(Runner):

    def __init__(self, project=None, max_workers=1):
        super().__init__(project, max_workers)
        self.executor = None
        self.futures = set()

    def _on_worker_done(self, future):
        if future.cancelled():
            return

        try:
            simulation = future.result()

        except WorkerCancelledError:
            self.options_cancelled_count += 1

        except:
            self.options_failed_count += 1

        else:
            self.project.add_simulation(simulation)
            self.options_simulated_count += 1

    def start(self):
        if self.executor is not None:
            raise RuntimeError('Already started')
        self.executor = concurrent.futures.ThreadPoolExecutor(self.max_workers)

    def shutdown(self, wait=True):
        if self.executor is None:
            return
        self.executor.shutdown(wait)
        self.executor = None

    def _submit(self, options):
        program = options.program
        worker = program.create_worker()

        future = self.executor.submit(worker.run, options)
        future.add_done_callback(self._on_worker_done)

        self.futures.add(future)
        self.options_submitted_count += 1

        return LocalTracker(options, worker, future)

    def wait(self, timeout=None):
        concurrent.futures.wait(self.futures, timeout, concurrent.futures.ALL_COMPLETED)
