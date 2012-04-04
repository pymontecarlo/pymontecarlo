#!/usr/bin/env python
"""
================================================================================
:mod:`queue` -- Queue of workers for running simulations
================================================================================

.. module:: queue
   :synopsis: Queue of workers for running simulations

.. inheritance-diagram:: pymontecarlo.runner.base.runner

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2012 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import os
import tempfile
import shutil
import logging
from Queue import Queue, Empty

# Third party modules.

# Local modules.

# Globals and constants variables.

def _iter_except(func, exception, first=None):
    """
    Call a function repeatedly until an exception is raised.
    From Python's recipe in **itertools** module.
    """
    try:
        if first is not None:
            yield first()
        while 1:
            yield func()
    except exception:
        pass

class Runner(object):
    def __init__(self, worker_class, workdir=None, overwrite=True,
                 nbprocesses=1, **kwargs):
        """
        Creates a new runner to run several simulations.
        
        Use :meth:`put` to add simulation to the run and then use the method
        :meth:`start` to start the simulation(s). 
        Status of the simulations can be retrieved using the method 
        :meth:`report`. 
        Results can also be retrieved as the simulations are completed using 
        :meth:`iter_results`.
        The method :meth:`join` before closing an application to ensure that
        all simulations were run and all workers are stopped.
        
        :arg worker_class: class of the worker to use to run the simulations
        
        :arg workdir: work directory for the simulation temporary files.
            If ``None``, a temporary folder is created and removed after all
            simulations are run. If not ``None``, the directory must exists.
        
        :arg overwrite: whether to overwrite already existing simulation file(s)
        
        :arg nbprocesses: number of processes/threads to use (default: 1)
        
        :arg **kwargs: other arguments to pass to the worker class during
            initialization
        """
        if nbprocesses < 1:
            raise ValueError, "Number of processes must be greater or equal to 1."
        self._nbprocesses = nbprocesses

        self._worker_class = worker_class

        if workdir is not None and not os.path.isdir(workdir):
            raise ValueError, 'Work directory (%s) is not a directory' % workdir
        self._workdir = workdir

        self._overwrite = overwrite
        self._kwargs = kwargs

        self._options_names = []
        self._queue_options = Queue()
        self._queue_results = Queue()
        self._workers = []

    def start(self):
        """
        Starts running the simulations.
        """
        if self._workers:
            raise RuntimeError, 'Already started'

        # Setup
        if self._workdir is None:
            self._workdir = tempfile.mkdtemp()
            self._user_defined_workdir = False
            logging.debug('Temporary work directory: %s', self._workdir)

        # Create workers
        self._workers = []
        for _ in range(self._nbprocesses):
            worker = self._worker_class(self._queue_options, self._queue_results,
                                        self._workdir, self._overwrite, **self._kwargs)
            self._workers.append(worker)

            worker.daemon = True
            worker.start()

    def stop(self):
        """
        Stops all the simulations in the queue.
        """
        for worker in self._workers:
            worker.stop()
        self._workers = []

        # Cleanup working directory if it was created in the __init__
        if not self._user_defined_workdir:
            shutil.rmtree(self._workdir, ignore_errors=True)
            logging.debug('Removed temporary work directory: %s', self._workdir)

    def put(self, options):
        """
        Puts an options in queue.
        
        An :exc:`ValueError` is raised if an options with the same name was
        already added. This error is raised has options with the same name 
        would lead to results been overwritten.
        """
        name = options.name
        if name in self._options_names:
            raise ValueError, 'An options with the name (%s) was already added' % name

        self._queue_options.put(options)
        self._options_names.append(name)

    def join(self):
        """
        Blocks until all items in the queue have been gotten and processed.
        """
        self._queue_options.join()
        self.stop()

    def is_alive(self):
        """
        Returns whether all options in the queue are simulated.
        """
        return self._queue_results.qsize() < len(self._options_names)

    def report(self):
        """
        Returns a tuple of:
        
          * counter of completed simulations
          * the progress of *one* of the currently running simulations 
              (between 0.0 and 1.0)
          * text indicating the status of *one* of the currently running 
              simulations
        """
        completed = self._queue_results.qsize()

        for worker in self._workers:
            progress, status = worker.report()
            if progress < 1.0:
                return completed, progress, status

        return completed, 0, ''

    def iter_results(self):
        """
        Returns an iterator over the results of the run. 
        
        .. note:: 
        
            Note that only the results of the completed simulations are returned.
            To be sure to get all the results, called :meth:`join()` before
            this method
            
        :return: results of each completed simulation
        :rtype: :class:`list` of :class:`Results <pymontecarlo.result.base.results.Results>`
        """
        return _iter_except(self._queue_results.get_nowait, Empty)

