#!/usr/bin/env python
"""
================================================================================
:mod:`base` -- Base interfaces for runners and creators
================================================================================

.. module:: base
   :synopsis: Base interfaces for runners and creators

.. inheritance-diagram:: pymontecarlo.runner.base

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2013 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import copy
import logging
import threading
from Queue import Empty

# Third party modules.

# Local modules.
from pymontecarlo.util.queue import Queue

# Globals and constants variables.

class _Runner(object):

    def __init__(self, program):
        """
        Creates a new runner to run several simulations.
        
        Use :meth:`put` to add simulation to the run and then use the method
        :meth:`start` to start the simulation(s). 
        Status of the simulations can be retrieved using the method 
        :meth:`report`. 
        The method :meth:`join` before closing an application to ensure that
        all simulations were run and all workers are stopped.
        
        :arg program: program used to run the simulations
        """
        self._program = program

        self._options_names = []
        self._queue_options = Queue()
        self._queue_results = Queue()

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

    def get_results(self):
        """
        Returns the results from the simulations.
        This is a blocking method which calls :meth:`join` before returning
        the results.
        
        :rtype: :class:`list`
        """
        self.join()

        results = []
        while True:
            try:
                results.append(self._queue_results.get_nowait())
            except Empty:
                break
        return results

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

class _RunnerDispatcher(threading.Thread):

    def __init__(self, program, queue_options, queue_results):
        threading.Thread.__init__(self)

        self._program = program
        self._queue_options = queue_options
        self._queue_results = queue_results

    def stop(self):
        """
        Stops running simulation.
        """
        threading.Thread.__init__(self)

    def report(self):
        """
        Returns a tuple of:
        
          * counter of completed simulations
          * the progress of *one* of the currently running simulations 
              (between 0.0 and 1.0)
          * text indicating the status of *one* of the currently running 
              simulations
        """
        return 0.0, ''

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

class _CreatorDispatcher(threading.Thread):

    def __init__(self, program, queue_options):
        threading.Thread.__init__(self)

        self._program = program
        self._queue_options = queue_options

    def stop(self):
        """
        Stops running simulation.
        """
        threading.Thread.__init__(self)
