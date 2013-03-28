#!/usr/bin/env python
"""
================================================================================
:mod:`creator` -- Queue of workers for creating simulation files
================================================================================

.. module:: creator
   :synopsis: Queue of workers for creating simulation files

.. inheritance-diagram:: pymontecarlo.runner.creator

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
import logging
import threading

# Third party modules.

# Local modules.
from pymontecarlo.util.queue import Queue

# Globals and constants variables.

class _Creator(object):

    def __init__(self, program):
        """
        Creates a new creator to create simulation files of several simulations.
        
        Use :meth:`put` to add simulation to the creation list and then use the
        method :meth:`start` to start the creation. 
        The method :meth:`join` before closing an application to ensure that
        all simulations were created and all workers are stopped.
        
        :arg program: program used to run the simulations
        
        :arg outputdir: output directory for the simulation files.
            The directory must exists.
        
        :arg overwrite: whether to overwrite already existing simulation file(s)
        
        :arg nbprocesses: number of processes/threads to use (default: 1)
        """
        self._program = program

        self._options_names = []
        self._queue_options = Queue()

    @property
    def program(self):
        """
        Program of this runner.
        """
        return self._program

    def put(self, options):
        """
        Puts an options in queue.
        
        An :exc:`ValueError` is raised if an options with the same name was
        already added. This error is raised has options with the same name 
        would lead to results been overwritten.
        
        .. note::
        
           A copy of the options is put in queue
           
        :arg options: options to be added to the queue
        """
        name = options.name
        if name in self._options_names:
            raise ValueError, 'An options with the name (%s) was already added' % name

        self._queue_options.put(copy.deepcopy(options))
        self._options_names.append(name)

        logging.debug('Options "%s" put in queue', name)

    def start(self):
        """
        Starts running the simulations.
        """
        raise NotImplementedError

    def stop(self):
        """
        Stops all running simulations.
        """
        raise NotImplementedError

    def is_alive(self):
        """
        Returns whether all options in the queue were simulated.
        """
        return not self._queue_options.are_all_tasks_done()

    def join(self):
        """
        Blocks until all options have been simulated.
        """
        self._queue_options.join()
        self.stop()
        self._options_names[:] = [] # clear

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
        return completed, 0, ''

class _Dispatcher(threading.Thread):

    def __init__(self, program, queue_options):
        threading.Thread.__init__(self)

        self._program = program
        self._queue_options = queue_options

    def stop(self):
        """
        Stops running simulation.
        """
        threading.Thread.__init__(self)

class _LocalDispatcher(_Dispatcher):

    def __init__(self, program, queue_options, outputdir, overwrite=True):
        _Dispatcher.__init__(self, program, queue_options)

        self._worker = program.worker_class()

        if not os.path.isdir(outputdir):
            raise ValueError, 'Output directory (%s) is not a directory' % outputdir
        self._outputdir = outputdir

        self._overwrite = overwrite

    def run(self):
        while True:
            try:
                # Retrieve options
                options = self._queue_options.get()

                # Check if options already exists
                xmlfilepath = os.path.join(self._outputdir, options.name + ".xml")
                if os.path.exists(xmlfilepath) and not self._overwrite:
                    logging.info('Skipping %s as options already exists', options.name)
                    self._queue_options.task_done()
                    continue

                # Run
                logging.debug('Running program specific worker')
                self._worker.reset()
                self._worker.create(options, self._outputdir)
                logging.debug('End program specific worker')

                self._queue_options.task_done()
            except Exception:
                self.stop()
                self._queue_options.raise_exception()

    def stop(self):
        self._worker.stop()
        _Dispatcher.stop(self)

class LocalCreator(_Creator):

    def __init__(self, program, outputdir, overwrite=True, nbprocesses=1):
        """
        Creates a new creator to create simulation files of several simulations.
        
        Use :meth:`put` to add simulation to the creation list and then use the
        method :meth:`start` to start the creation. 
        The method :meth:`join` before closing an application to ensure that
        all simulations were created and all workers are stopped.
        
        :arg program: program used to run the simulations
        
        :arg outputdir: output directory for the simulation files.
            The directory must exists.
        
        :arg overwrite: whether to overwrite already existing simulation file(s)
        
        :arg nbprocesses: number of processes/threads to use (default: 1)
        """
        _Creator.__init__(self, program)

        if nbprocesses < 1:
            raise ValueError, "Number of processes must be greater or equal to 1."
        self._nbprocesses = nbprocesses

        if not os.path.isdir(outputdir):
            raise ValueError, 'Output directory (%s) is not a directory' % outputdir
        self._outputdir = outputdir

        self._overwrite = overwrite

        self._dispatchers = []

    @property
    def outputdir(self):
        """
        Output directory.
        """
        return self._outputdir

    def start(self):
        """
        Starts running the simulations.
        """
        if self._dispatchers:
            raise RuntimeError, 'Already started'

        # Create dispatchers
        self._dispatchers = []
        for _ in range(self._nbprocesses):
            dispatcher = \
                _LocalDispatcher(self.program, self._queue_options,
                                 self._outputdir, self._overwrite)
            self._dispatchers.append(dispatcher)

            dispatcher.daemon = True
            dispatcher.start()
            logging.debug('Started dispatcher: %s', dispatcher.name)

    def stop(self):
        """
        Stops all dispatchers and closes the current runner.
        """
        for dispatcher in self._dispatchers:
            dispatcher.stop()
        self._dispatchers = []

