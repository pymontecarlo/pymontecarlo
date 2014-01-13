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
import threading
import atexit
from Queue import Empty

# Third party modules.

# Local modules.
from pymontecarlo.util.queue import Queue
from pymontecarlo.results.results import Results

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
        """
        self._program = program
        self._converter = program.converter_class()

        self._options_lookup = {}
        self._options_names = []
        self._queue_options = Queue()

        atexit.register(self.close) # Ensures that the runner is properly closed

    def put(self, options):
        """
        Puts an options in queue.
        The options are converted using the converter of this runner's program.

        An :exc:`ValueError` is raised if an options with the same name was
        already added.
        This error is raised as options with the same name would lead to
        results been overwritten.

        :arg options: options to be added to the queue
        """
        base_options = options
        list_options = self._converter.convert(base_options)
        if not list_options:
            raise ValueError, 'Options not compatible with this program'

        for options in list_options:
            name = options.name
            if name in self._options_names:
                raise ValueError, \
                        'An options with the name (%s) was already added' % name

            self._queue_options.put(options)
            self._options_names.append(name)

            self._options_lookup.setdefault(base_options, []).append(options.uuid)

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exctype, value, tb):
        self.close()

    def start(self):
        """
        Starts running the simulations.
        """
        raise NotImplementedError

    def stop(self):
        """
        Stops all running simulations.
        The simulations can be restarted by calling :meth:`start`.
        """
        raise NotImplementedError

    def close(self):
        """
        Stops all running simulations and closes the runner.
        The runner cannot be restarted after calling :meth:`close`.
        """
        raise NotImplementedError

    def is_alive(self):
        """
        Returns whether simulations are being executed.
        """
        return not self._queue_options.are_all_tasks_done()

    def join(self):
        """
        Blocks until all options have been simulated.
        """
        self._queue_options.join()
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

    @property
    def program(self):
        """
        Program of this runner.
        """
        return self._program

class _Runner(_Creator):

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
        _Creator.__init__(self, program)

        self._queue_results = Queue()

    def get_results(self):
        """
        Returns the results from the simulations.
        This is a blocking method which calls :meth:`join` before returning
        the results.
        The order of the results may not match the order in which they were
        put in queue.

        :rtype: :class:`list` of :class:`.Results`
        """
        self.join()

        # Get results from queue
        raw_results = {}
        while True:
            try:
                results = self._queue_results.get_nowait()
                raw_results[results.options.uuid] = results
            except Empty:
                break

        # Separate results
        group_results = []
        for base_options, uuids in self._options_lookup.iteritems():
            list_results = []
            for uuid in uuids:
                results = raw_results[uuid]
                list_results.append((results.options, results[0]))

            group_results.append(Results(base_options, list_results))

        self._options_lookup.clear()

        return group_results

class _CreatorDispatcher(threading.Thread):

    def __init__(self, program, queue_options):
        threading.Thread.__init__(self)

        self._program = program
        self._queue_options = queue_options

    def stop(self):
        """
        Stops running simulation.
        """
        pass

    def close(self):
        """
        Stops running simulation and closes this dispatcher.
        """
        pass

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

class _RunnerDispatcher(_CreatorDispatcher):

    def __init__(self, program, queue_options, queue_results):
        _CreatorDispatcher.__init__(self, program, queue_options)

        self._queue_results = queue_results

