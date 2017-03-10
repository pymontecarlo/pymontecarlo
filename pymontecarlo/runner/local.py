"""
Local runner.
"""

# Standard library modules.
import os
import concurrent.futures
import tempfile
import shutil

# Third party modules.

# Local modules.
from pymontecarlo.runner.base import Runner, Tracker
from pymontecarlo.exceptions import WorkerCancelledError

# Globals and constants variables.

class LocalTracker(Tracker):

    def __init__(self, simulation, worker, future):
        super().__init__(simulation)
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

    def _create_output_dir(self, simulation):
        if self.project.filepath is not None:
            head, tail = os.path.split(self.project.filepath)
            simsdirname = os.path.splitext(tail)[0] + '_simulations'
            simdirname = simulation.identifier
            outputdir = os.path.join(head, simsdirname, simdirname)
            os.makedirs(outputdir, exist_ok=True)
            return outputdir, False

        else:
            return tempfile.mkdtemp(), True

    def _run(self, worker, simulation, outputdir, temporary):
        try:
            worker.run(simulation, outputdir)

        finally:
            if temporary:
                shutil.rmtree(outputdir, ignore_errors=True)

        return simulation

    def _submit(self, simulation):
        program = simulation.options.program
        worker = program.create_worker()
        outputdir, temporary = self._create_output_dir(simulation)

        future = self.executor.submit(self._run, worker, simulation, outputdir, temporary)
        future.add_done_callback(self._on_worker_done)
        self.futures.add(future)

        return LocalTracker(simulation, worker, future)

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
