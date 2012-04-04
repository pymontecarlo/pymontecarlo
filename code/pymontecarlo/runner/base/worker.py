#!/usr/bin/env python
"""
================================================================================
:mod:`worker` -- Base worker
================================================================================

.. module:: worker
   :synopsis: Base worker

.. inheritance-diagram:: pymontecarlo.runner.base.worker

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2012 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import os
import threading

# Third party modules.

# Local modules.

# Globals and constants variables.

class InvalidPlatform(Exception):
    pass

class Worker(threading.Thread):
    def __init__(self, queue_options, queue_results, workdir, overwrite=True):
        """
        Base class for all runners. A runner is used to run one **or many** 
        simulations with a given program.
        
        To start a runner, execute the method :meth:`start()`.
        The method :meth:`report()` can be used to retrieve the progress.
        
        :arg options: options of the simulation or :class:`list` of options of
            several simulations. The order of the simulations is preserved.
        :type options: :class:`Options <pymontecarlo.input.base.options.Options>`
            or :class:`list` of :class:`Options <pymontecarlo.input.base.options.Options>`
        
        :arg workdir: work directory for temporary files created during the 
            simulation(s). The directory must exists.
        
        :arg overwrite: whether to overwrite results if they exist
            (default: ``True``)
        """
        threading.Thread.__init__(self)

        self._queue_options = queue_options
        self._queue_results = queue_results

        if not os.path.isdir(workdir):
            raise ValueError, 'Work directory (%s) is not a directory' % workdir
        self._workdir = workdir

        self._overwrite = overwrite

        self._reset()

    def _reset(self):
        """
        Resets the worker. This method is called before starting a run.
        """
        self._progress = 0.0
        self._status = ''

    def create(self):
        """
        Creates all simulation files without starting the simulation(s).
        All simulations in the options queue will be created.
        The simulation files created will depend on the Monte Carlo program used.
        The simulation files could also be a folder.
        The simulation files are saved in the *work directory*.
        """
        while True:
            options = self._queue_options.get()
            filepath = self._create(options)

            self._queue_results.put(filepath)

            self._queue_options.task_done()

    def _create(self, options):
        """
        Creates the simulation files from the options.
        This method should be implemented by derived class. 
        """
        raise NotImplementedError

    def run(self):
        """
        Creates and runs all simulations in the options queue.
        The results from the simulations are stored in the results queue.
        """
        while True:
            self._reset()

            self._progress = 0.0
            self._status = 'Starting'

            options = self._queue_options.get()
            self._run(options)

            results = self._get_results(options)
            self._queue_results.put(results)

            self._progress = 1.0
            self._status = 'Completed'

            self._queue_options.task_done()

    def _run(self, options):
        """
        Creates and runs a simulation from the specified options.
        This method should be implemented by derived class.
        """
        raise NotImplementedError

    def _get_results(self, options):
        """
        Generates and returns the results from the simulation outputs.
        """
        raise NotImplementedError

    def stop(self):
        """
        Stops all simulations.
        """
        self._status = 'Stopped'

    def report(self):
        """
        Returns a tuple of:
        
          * the progress of the current running simulation (between 0.0 and 1.0)
          * text indicating the status of the current running simulation
        """
        return self._progress, self._status

    def _get_filepath(self, options, ext='xml'):
        """
        Returns a filepath from the work directory, name of the options, 
        extension.
        """
        return os.path.join(self._workdir, options.name + "." + ext)

class SubprocessWorker(Worker):
    def _reset(self):
        Worker._reset(self)
        self._process = None

    def stop(self):
        Worker.stop(self)
        if self._process is not None:
            self._process.kill()

