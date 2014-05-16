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
import logging
import threading
import queue
from collections import Counter
from operator import itemgetter
import copy

# Third party modules.

# Local modules.
from pymontecarlo.util.monitorable import _Monitorable, _MonitorableThread
from pymontecarlo.util.signal import Signal
from pymontecarlo.util.parameter import freeze

# Globals and constants variables.

class _Runner(_Monitorable):

    STATE_QUEUED = 'queued'
    STATE_RUNNING = 'running'
    STATE_SIMULATED = 'simulated'
    STATE_ERROR = 'error'

    def __init__(self, max_workers=1):
        _Monitorable.__init__(self)

        if max_workers < 1:
            raise ValueError("Number of workers must be greater or equal to 1.")

        self._is_started = threading.Event()

        # State
        self._options_state_lock = threading.Lock()
        self._options_state = {}

        # Queues
        self._queue_options = queue.Queue()
        self._queue_results = queue.Queue()

        # Signals
        self.options_added = Signal()
        self.options_running = Signal()
        self.options_simulated = Signal()
        self.options_error = Signal()
        self.results_saved = Signal()
        self.results_error = Signal()

        self.options_added.connect(self._on_options_added)
        self.options_running.connect(self._on_options_running)
        self.options_simulated.connect(self._on_options_simulated)
        self.options_error.connect(self._on_options_error)
        self.results_error.connect(self._on_results_error)

        # Dispatchers
        self._dispatchers_options = set()
        for _ in range(max(1, max_workers - 1)):
            dispatcher = self._create_options_dispatcher()
            dispatcher.options_running.connect(self.options_running)
            dispatcher.options_simulated.connect(self.options_simulated)
            dispatcher.options_error.connect(self.options_error)
            self._dispatchers_options.add(dispatcher)

        self._dispatchers_results = set()
        dispatcher = self._create_results_dispatcher()
        dispatcher.results_saved.connect(self.results_saved)
        dispatcher.results_error.connect(self.results_error)
        self._dispatchers_results.add(dispatcher)

        self._dispatchers = self._dispatchers_options | self._dispatchers_results

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exctype, value, tb):
        self.close()
        return False

    def _start(self):
        """
        Starts running the simulations.
        """
        if self._is_started.is_set():
            raise RuntimeError('Runner already started')

        for dispatcher in self._dispatchers:
            dispatcher.start()
            logging.debug('Start dispatcher: %s' % dispatcher)

        self._is_started.set()

    def _create_options_dispatcher(self):
        raise NotImplementedError

    def _create_results_dispatcher(self):
        raise NotImplementedError

    def start(self):
        self._start()

    def cancel(self):
        """
        Cancels all running simulations.
        """
        for dispatcher in self._dispatchers:
            dispatcher.cancel()
            logging.debug('Dispatcher cancelled: %s' % dispatcher)

    def is_alive(self):
        """
        Returns whether simulations are being executed.
        """
        for dispatcher in self._dispatchers:
            if not dispatcher.is_alive():
                return False
        return True

    def join(self):
        """
        Blocks until all options have been simulated.
        """
        for dispatcher in self._dispatchers:
            dispatcher.raise_exception()

        self._queue_options.join()
        self._queue_results.join()

        for dispatcher in self._dispatchers:
            dispatcher.raise_exception()

    def close(self):
        """
        Wait for simulation(s) to finish and closes the runner.
        """
        self.cancel()
        for dispatcher in self._dispatchers:
            dispatcher.join()

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
        if not options.programs:
            raise ValueError('No program associated with options')

        base_options = copy.deepcopy(options)
        logging.debug('Putting %s options is queue' % base_options)

        list_options = []
        for program in base_options.programs:
            converter = program.converter_class()

            for options in converter.convert(base_options):
                options.programs.clear()
                options.programs.add(program)
                options.name = options.name + '+' + program.alias
                freeze(options)

                self._queue_options.put((base_options, options))
                list_options.append(options)
                self.options_added.fire(options)

        return list_options

    def _on_options_added(self, options):
        logging.debug('Options %s added' % options)
        with self._options_state_lock:
            self._options_state[options] = (self.STATE_QUEUED, 'queued')

    def _on_options_running(self, options):
        logging.debug('Options %s running' % options)
        with self._options_state_lock:
            self._options_state[options] = (self.STATE_RUNNING, 'running')

    def _on_options_simulated(self, options):
        logging.debug('Options %s simulated' % options)
        with self._options_state_lock:
            self._options_state[options] = (self.STATE_SIMULATED, 'simulated')

    def _on_options_error(self, options, ex):
        logging.exception("Options %s error" % options)
        with self._options_state_lock:
            self._options_state[options] = (self.STATE_ERROR, str(ex))

    def _on_results_error(self, results, ex):
        logging.exception("Results %s error" % results)
        with self._options_state_lock:
            for container in results:
                self._options_state[container.options] = (self.STATE_ERROR, str(ex))

    def options_state(self, options):
        with self._options_state_lock:
            return self._options_state[options][0]

    def options_progress(self, options):
        with self._options_state_lock:
            state, _message = self._options_state[options]

        if state == self.STATE_SIMULATED:
            return 1.0
        elif state == self.STATE_RUNNING:
            for dispatcher in self._dispatchers_options:
                if dispatcher.current_options != options:
                    continue
                return dispatcher.progress
        else:
            return 0.0

    def options_status(self, options):
        with self._options_state_lock:
            state, message = self._options_state[options]

        if state == self.STATE_RUNNING:
            for dispatcher in self._dispatchers_options:
                if dispatcher.current_options != options:
                    continue
                return dispatcher.status
        else:
            return message

    @property
    def progress(self):
        with self._options_state_lock:
            counter = Counter(map(itemgetter(0), self._options_state.values()))
            simulated = counter[self.STATE_SIMULATED]
            error = counter[self.STATE_ERROR]
            total = len(self._options_state)
            return (simulated + error) / total

    @property
    def status(self):
        if not self._is_started.is_set():
            return 'not started'
        elif self.is_cancelled():
            return 'cancelled'
        elif self.is_exception_raised():
            return 'error occurred'
        elif self.is_alive():
            return 'running'
        else:
            return 'unknown'

class _RunnerDispatcher(_MonitorableThread):
    pass

class _RunnerOptionsDispatcher(_RunnerDispatcher):

    def __init__(self, queue_options, queue_results):
        _RunnerDispatcher.__init__(self)

        self._queue_options = queue_options
        self._queue_results = queue_results

        self.options_running = Signal()
        self.options_simulated = Signal()
        self.options_error = Signal()

    @property
    def current_options(self):
        raise NotImplementedError

class _RunnerResultsDispatcher(_RunnerDispatcher):

    def __init__(self, queue_results):
        _RunnerDispatcher.__init__(self)

        self._queue_results = queue_results

        self.results_saved = Signal()
        self.results_error = Signal()


#class _Creator(object):
#
#    def __init__(self, program):
#        """
#        Creates a new creator to create simulation files of several simulations.
#
#        Use :meth:`put` to add simulation to the creation list and then use the
#        method :meth:`start` to start the creation.
#        The method :meth:`join` before closing an application to ensure that
#        all simulations were created and all workers are stopped.
#
#        :arg program: program used to run the simulations
#        """
#        self._program = program
#        self._converter = program.converter_class()
#
#        self._options_lookup = {}
#        self._options_names = []
#        self._queue_options = Queue()
#
#        atexit.register(self.close) # Ensures that the runner is properly closed
#
#    def put(self, options):
#        """
#        Puts an options in queue.
#        The options are converted using the converter of this runner's program.
#
#        An :exc:`ValueError` is raised if an options with the same name was
#        already added.
#        This error is raised as options with the same name would lead to
#        results been overwritten.
#
#        :arg options: options to be added to the queue
#        """
#        base_options = options
#        list_options = self._converter.convert(base_options)
#        if not list_options:
#            raise ValueError('Options not compatible with this program')
#
#        for options in list_options:
#            name = options.name
#            if name in self._options_names:
#                raise ValueError('An options with the name (%s) was already added' % name)
#
#            self._queue_options.put(options)
#            self._options_names.append(name)
#
#            self._options_lookup.setdefault(base_options, []).append(options.uuid)
#
#    def __enter__(self):
#        self.start()
#        return self
#
#    def __exit__(self, exctype, value, tb):
#        self.close()
#
#    def start(self):
#        """
#        Starts running the simulations.
#        """
#        raise NotImplementedError
#
#    def stop(self):
#        """
#        Stops all running simulations.
#        The simulations can be restarted by calling :meth:`start`.
#        """
#        raise NotImplementedError
#
#    def close(self):
#        """
#        Stops all running simulations and closes the runner.
#        The runner cannot be restarted after calling :meth:`close`.
#        """
#        raise NotImplementedError
#
#    def is_alive(self):
#        """
#        Returns whether simulations are being executed.
#        """
#        return not self._queue_options.are_all_tasks_done()
#
#    def join(self):
#        """
#        Blocks until all options have been simulated.
#        """
#        self._queue_options.join()
#        self._options_names[:] = [] # clear
#
#    def report(self):
#        """
#        Returns a tuple of:
#
#          * counter of completed simulations
#          * the progress of *one* of the currently running simulations
#              (between 0.0 and 1.0)
#          * text indicating the status of *one* of the currently running
#              simulations
#        """
#        completed = len(self._options_names) - self._queue_options.unfinished_tasks
#        return completed, 0, ''
#
#    @property
#    def program(self):
#        """
#        Program of this runner.
#        """
#        return self._program

#class _Runner(_Creator):
#
#    def __init__(self, program):
#        """
#        Creates a new runner to run several simulations.
#
#        Use :meth:`put` to add simulation to the run and then use the method
#        :meth:`start` to start the simulation(s).
#        Status of the simulations can be retrieved using the method
#        :meth:`report`.
#        The method :meth:`join` before closing an application to ensure that
#        all simulations were run and all workers are stopped.
#
#        :arg program: program used to run the simulations
#        """
#        _Creator.__init__(self, program)
#
#        self._queue_results = Queue()
#
#    def get_results(self):
#        """
#        Returns the results from the simulations.
#        This is a blocking method which calls :meth:`join` before returning
#        the results.
#        The order of the results may not match the order in which they were
#        put in queue.
#
#        :rtype: :class:`list` of :class:`.Results`
#        """
#        self.join()
#
#        # Get results from queue
#        raw_results = {}
#        while True:
#            try:
#                results = self._queue_results.get_nowait()
#                raw_results[results.options.uuid] = results
#            except Empty:
#                break
#
#        # Separate results
#        group_results = []
#        for base_options, uuids in self._options_lookup.items():
#            list_results = []
#            for uuid in uuids:
#                results = raw_results[uuid]
#                list_results.append((results.options, results[0]))
#
#            group_results.append(Results(base_options, list_results))
#
#        self._options_lookup.clear()
#
#        return group_results
#
#class _CreatorDispatcher(threading.Thread):
#
#    def __init__(self, program, queue_options):
#        threading.Thread.__init__(self)
#
#        self._program = program
#        self._queue_options = queue_options
#
#    def stop(self):
#        """
#        Stops running simulation.
#        """
#        pass
#
#    def close(self):
#        """
#        Stops running simulation and closes this dispatcher.
#        """
#        pass
#
#    def report(self):
#        """
#        Returns a tuple of:
#
#          * counter of completed simulations
#          * the progress of *one* of the currently running simulations
#              (between 0.0 and 1.0)
#          * text indicating the status of *one* of the currently running
#              simulations
#        """
#        return 0.0, ''
#
#class _RunnerDispatcher(_CreatorDispatcher):
#
#    def __init__(self, program, queue_options, queue_results):
#        _CreatorDispatcher.__init__(self, program, queue_options)
#
#        self._queue_results = queue_results

