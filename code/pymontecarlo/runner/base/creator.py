#!/usr/bin/env python
"""
================================================================================
:mod:`creator` -- Queue of workers for creating simulation files
================================================================================

.. module:: creator
   :synopsis: Queue of workers for creating simulation files

.. inheritance-diagram:: pymontecarlo.runner.base.creator

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2012 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import os
from Queue import Queue

# Third party modules.

# Local modules.

# Globals and constants variables.


class Creator(object):
    def __init__(self, worker_class, outputdir, overwrite=True,
                 nbprocesses=1, **kwargs):
        """
        Creates a new creator to create simulation files of several simulations.
        
        Use :meth:`put` to add simulation to the creation list and then use the
         method :meth:`start` to start the creation. 
        The method :meth:`join` before closing an application to ensure that
        all simulations were created and all workers are stopped.
        
        :arg worker_class: class of the worker to use to run the simulations
        
        :arg outputdir: output directory for the simulation files.
            The directory must exists.
        
        :arg overwrite: whether to overwrite already existing simulation file(s)
        
        :arg nbprocesses: number of processes/threads to use (default: 1)
        
        :arg **kwargs: other arguments to pass to the worker class during
            initialization
        """
        if nbprocesses < 1:
            raise ValueError, "Number of processes must be greater or equal to 1."
        self._nbprocesses = nbprocesses

        self._worker_class = worker_class

        if not os.path.isdir(outputdir):
            raise ValueError, 'Output directory (%s) is not a directory' % outputdir
        self._outputdir = outputdir

        self._overwrite = overwrite
        self._kwargs = kwargs

        self._options_names = []
        self._queue_options = Queue()
        self._queue_results = Queue()
        self._workers = []

    def start(self):
        """
        Starts creating the simulations.
        """
        if self._workers:
            raise RuntimeError, 'Already started'

        # Create workers
        self._workers = []
        for _ in range(self._nbprocesses):
            worker = self._worker_class(self._queue_options, self._queue_results,
                                        self._outputdir, self._overwrite,
                                        **self._kwargs)
            worker.run = worker.create # Replace threading run by create method

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
        
          * counter of created simulations
          * always 0.0
          * always empty string
        """
        return self._queue_results.qsize(), 0.0, ''
