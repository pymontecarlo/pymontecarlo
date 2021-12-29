"""
Local runner.
"""

# Standard library modules.
import os
import tempfile
import shutil
import asyncio
import shutil
import logging

# Third party modules.

# Local modules.
from pymontecarlo.runner.base import SimulationRunnerBase

# Globals and constants variables.
logger = logging.getLogger(__name__)


class LocalWorkerDispatcher:
    def __init__(self, project, token, queue):
        self.project = project
        self.token = token
        self.queue = queue

    async def run(self):
        logger.debug("Dispatcher running")

        while True:
            # Check for recalculation
            if (
                self.project.recalculate_required
                and self.queue.empty()
                and self.queue._finished.is_set()
            ):
                # Create new token
                token = self.token.create_subtoken("Recalculate")

                # Recalculate
                logger.debug("Starting recalculation of project")
                await self.project.recalculate(token)
                logger.debug("Recalculation done")

            # Get simulation or wait until the next one is available
            logger.debug("Awaiting for simulation")

            simulation = await self.queue.get()

            logger.debug(
                'Simulation "{}" retrieved from in queue'.format(simulation.identifier)
            )

            # Create output directory
            if self.project.filepath is not None:
                head, tail = os.path.split(self.project.filepath)
                dirname = os.path.splitext(tail)[0] + "_simulations"
                outputdir = os.path.join(head, dirname, simulation.identifier)

                if os.path.exists(outputdir) and os.listdir(outputdir):
                    logger.debug("Removing content in {}".format(outputdir))
                    shutil.rmtree(outputdir, ignore_errors=True)

                temporary = False
            else:
                outputdir = tempfile.mkdtemp()
                temporary = True

            os.makedirs(outputdir, exist_ok=True)
            logger.debug("Created output directory: {}".format(outputdir))

            # Run
            try:
                # Create worker
                worker = simulation.options.program.worker

                # Create token
                token = self.token.create_subtoken(
                    simulation.identifier, category="simulation"
                )

                logger.debug(
                    'Launching worker "{!r}" of simulation "{}"'.format(
                        worker, simulation.identifier
                    )
                )

                await worker.run(token, simulation, outputdir)

                logger.debug('Worker "{!r}" successfully terminated'.format(worker))

            finally:
                # Set "task done" flag
                self.queue.task_done()

                # Remove temporary folder
                if temporary:
                    shutil.rmtree(outputdir, ignore_errors=True)
                    logger.debug(
                        "Removed temporary output directory: {}".format(outputdir)
                    )

            # Simulation succeeded, so add to project
            self.project.add_simulation(simulation)
            logger.debug(
                'Simulation "{}" added to project'.format(simulation.identifier)
            )


class LocalSimulationRunner(SimulationRunnerBase):
    def __init__(self, project=None, token=None, max_workers=1):
        super().__init__(project, token, max_workers)

        # Create queues
        self._queue = asyncio.Queue()

        # Create dispatchers
        self._dispatchers = []

        for _ in range(max_workers):
            dispatcher = LocalWorkerDispatcher(self.project, self.token, self._queue)
            self._dispatchers.append(dispatcher)

        self._tasks = []

    async def _submit(self, simulation):
        await self._queue.put(simulation)

    async def start(self):
        # Check if already running
        if self._tasks:
            logger.debug("Already started")
            return

        # Create task for dispatchers
        for dispatcher in self._dispatchers:
            # Use ensure_future instead of create_task, because the latter does not work with qasync.
            # It does not seem to have any influence on the normal operation of the runner.
            task = asyncio.ensure_future(dispatcher.run())
            self._tasks.append(task)

        logger.debug("Runner started")

    async def shutdown(self):
        logger.debug("Starting shutdown")

        await self._queue.join()

        await self.cancel()

        logger.debug("Runner is shutdown")

    async def cancel(self):
        logger.debug("Starting cancellation")

        for task in self._tasks:
            task.cancel()

        # Wait until all dispatchers are cancelled.
        logger.debug("Waiting for dispatchers to cancel")

        await asyncio.gather(*self._tasks, return_exceptions=True)

        self._tasks.clear()

        logger.debug("All dispatchers are cancelled")

        # Empty queue
        logging.debug("Emptying queue")

        while not self._queue.empty():
            await self._queue.get()
            self._queue.task_done()

        logging.debug("Queue was emptied")

    async def set_project(self, project):
        await super().set_project(project)

        # Update dispatcher
        for dispatcher in self._dispatchers:
            dispatcher.project = project
