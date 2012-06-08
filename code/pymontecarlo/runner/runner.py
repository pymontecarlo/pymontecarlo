#!/usr/bin/env python
"""
================================================================================
:mod:`queue` -- Queue of workers for running simulations
================================================================================

.. module:: queue
   :synopsis: Queue of workers for running simulations

.. inheritance-diagram:: pymontecarlo.runner.runner

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2012 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import os
import copy
from operator import methodcaller

# Third party modules.

# Local modules.
from pymontecarlo.runner.queue import OptionsQueue

# Globals and constants variables.

class Runner(object):
    def __init__(self, worker_class, outputdir, workdir=None, overwrite=True,
                 nbprocesses=1, **kwargs):
        """
        Creates a new runner to run several simulations.
        
        Use :meth:`put` to add simulation to the run and then use the method
        :meth:`start` to start the simulation(s). 
        Status of the simulations can be retrieved using the method 
        :meth:`report`. 
        The method :meth:`join` before closing an application to ensure that
        all simulations were run and all workers are stopped.
        
        :arg worker_class: class of the worker to use to run the simulations
        
        :arg outputdir: output directory for saving the results from the 
            simulation. The directory must exists.
        
        :arg workdir: work directory for the simulation temporary files.
            If ``None``, a temporary folder is created and removed after each
            simulation is run. If not ``None``, the directory must exists.
        
        :arg overwrite: whether to overwrite already existing simulation file(s)
        
        :arg nbprocesses: number of processes/threads to use (default: 1)
        
        :arg kwargs: other arguments to pass to the worker class during
            initialization
        """
        if nbprocesses < 1:
            raise ValueError, "Number of processes must be greater or equal to 1."
        self._nbprocesses = nbprocesses

        self._worker_class = worker_class

        if not os.path.isdir(outputdir):
            raise ValueError, 'Output directory (%s) is not a directory' % outputdir
        self._outputdir = outputdir

        if workdir is not None and not os.path.isdir(workdir):
            raise ValueError, 'Work directory (%s) is not a directory' % workdir
        self._workdir = workdir

        self._overwrite = overwrite
        self._kwargs = kwargs

        self._options_names = []
        self._queue_options = OptionsQueue()
        self._workers = []

    def start(self):
        """
        Starts running the simulations.
        """
        if self._workers:
            raise RuntimeError, 'Already started'

        # Create workers
        self._workers = []
        for _ in range(self._nbprocesses):
            worker = self._worker_class(self._queue_options, self._outputdir,
                                        self._workdir, self._overwrite,
                                        **self._kwargs)
            self._workers.append(worker)

            worker.daemon = True
            worker.start()

    def put(self, options):
        """
        Puts an options in queue.
        
        An :exc:`ValueError` is raised if an options with the same name was
        already added. This error is raised has options with the same name 
        would lead to results been overwritten.
        
        .. note::
        
           A copy of the options is put in queue to prevent actions of a worker 
           to affect another one
           
        :arg options: options to be added to the queue
        """
        name = options.name
        if name in self._options_names:
            raise ValueError, 'An options with the name (%s) was already added' % name

        self._queue_options.put(copy.deepcopy(options))
        self._options_names.append(name)

    def stop(self):
        """
        Stops all workers and closes the current runner.
        """
        for worker in self._workers:
            worker.stop()
        self._workers = []

    def is_alive(self):
        """
        Returns whether all options in the queue are simulated.
        """
        all_workers_alive = all(map(methodcaller('is_alive'), self._workers))
        all_tasks_done = self._queue_options.are_all_tasks_done()

        return all_workers_alive and not all_tasks_done

    def join(self):
        """
        Blocks until all options have been simulated.
        """
        self._queue_options.join()
        self.close()

    def report(self):
        """
        Returns a tuple of:
        
          * counter of completed simulations
          * the progress of *one* of the currently running simulations 
              (between 0.0 and 1.0)
          * text indicating the status of *one* of the currently running 
              simulations
        """
        completed = len(self._options_names) - self._queue_options.unfinished_tasks

        for worker in self._workers:
            progress, status = worker.report()
            if progress > 0.0 and progress < 1.0: # active worker
                return completed, progress, status

        return completed, 0, ''

