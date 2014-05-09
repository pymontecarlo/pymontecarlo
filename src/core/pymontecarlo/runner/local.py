#!/usr/bin/env python
"""
================================================================================
:mod:`local` -- Local runner and creator
================================================================================

.. module:: local
   :synopsis: Local runner and creator

.. inheritance-diagram:: pymontecarlo.runner.local

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2013 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import os
import logging
import tempfile
import shutil
import queue

# Third party modules.

# Local modules.
from pymontecarlo.runner.base import \
    _Runner, _RunnerOptionsDispatcher, _RunnerResultsDispatcher
from pymontecarlo.results.results import Results
from pymontecarlo.fileformat.results.results import \
    append as append_results

# Globals and constants variables.

class _LocalRunnerOptionsDispatcher(_RunnerOptionsDispatcher):

    def __init__(self, program, queue_options, queue_results,
                 outputdir, workdir=None):
        _RunnerOptionsDispatcher.__init__(self, program, queue_options, queue_results)

        self._worker = program.worker_class(program)

        self._outputdir = outputdir
        self._workdir = workdir
        self._user_defined_workdir = self._workdir is not None

    def run(self):
        while not self._force_cancel.is_set():
            try:
                # Retrieve options
                try:
                    base_options, options = self._queue_options.get(timeout=1)
                except queue.Empty:
                    continue

                # Create working directory
                if not self._user_defined_workdir:
                    workdir = tempfile.mkdtemp()
                else:
                    workdir = self._workdir
                logging.debug('Work directory: %s', workdir)

                # Run
                logging.debug('Running program specific worker')

                self._worker.reset()
                results = self._worker.run(options, self._outputdir, workdir)

                logging.debug('End program specific worker')

                # Cleanup
                if not self._user_defined_workdir:
                    shutil.rmtree(workdir, ignore_errors=True)
                    logging.debug('Removed temporary work directory: %s', workdir)

                # Put results in queue
                self._queue_results.put(Results(base_options, [results]))

                self._queue_options.task_done()
            except:
                logging.critical('Exception in dispatcher', exc_info=True)
                self._queue_options.task_done()
                break

        self._is_cancelled.set()

    def cancel(self):
        self._worker.cancel()
        _RunnerOptionsDispatcher.cancel(self)

    def report(self):
        return self._worker.report()

class _LocalRunnerResultsDispatcher(_RunnerResultsDispatcher):

    def __init__(self, program, queue_results, outputdir):
        _RunnerResultsDispatcher.__init__(self, program, queue_results)

        self._outputdir = outputdir

    def run(self):
        while not self._force_cancel.is_set():
            try:
                # Retrieve results
                try:
                    results = self._queue_results.get(timeout=1)
                except queue.Empty:
                    continue

                h5filepath = os.path.join(self._outputdir,
                                          results.options.name + '.h5')

                if os.path.exists(h5filepath):
                    append_results(results, h5filepath)
                else:
                    results.write(h5filepath)

                self._queue_results.task_done()
            except:
                logging.critical('Exception in dispatcher', exc_info=True)
                self._queue_results.task_done()
                break

        self._is_cancelled.set()

class LocalRunner(_Runner):

    def __init__(self, program, outputdir, workdir=None, overwrite=True,
                 max_workers=1):
        """
        Creates a new runner to run several simulations.

        Use :meth:`put` to add simulation to the run and then use the method
        :meth:`start` to start the simulation(s).
        Status of the simulations can be retrieved using the method
        :meth:`report`.
        The method :meth:`join` before closing an application to ensure that
        all simulations were run and all workers are stopped.

        :arg program: program used to run the simulations

        :arg outputdir: output directory for saving the results from the
            simulation. The directory must exists.

        :arg workdir: work directory for the simulation temporary files.
            If ``None``, a temporary folder is created and removed after each
            simulation is run. If not ``None``, the directory must exists.

        :arg overwrite: whether to overwrite already existing simulation file(s)

        :arg nbprocesses: number of processes/threads to use (default: 1)
        """
        _Runner.__init__(self, program, max_workers)

        if not os.path.isdir(outputdir):
            raise ValueError('Output directory (%s) is not a directory' % outputdir)
        self._outputdir = outputdir

        if workdir is not None and not os.path.isdir(workdir):
            raise ValueError('Work directory (%s) is not a directory' % workdir)

        self._overwrite = overwrite

        # Create dispatchers
        for _ in range(max(1, max_workers - 1)):
            dispatcher = \
                _LocalRunnerOptionsDispatcher(program, self._queue_options,
                                              self._queue_results, outputdir,
                                              workdir)
            self._dispatchers_options.add(dispatcher)

        dispatcher = _LocalRunnerResultsDispatcher(program, self._queue_results,
                                                   outputdir)
        self._dispatchers_results.add(dispatcher)

    def put(self, options):
        h5filepath = os.path.join(self._outputdir, options.name + '.h5')
        if os.path.exists(h5filepath) and not self._overwrite:
            logging.info('Skipping %s as results already exists', options.name)
            return

        _Runner.put(self, options)

#class _LocalCreatorDispatcher(_CreatorDispatcher):
#
#    def __init__(self, program, queue_options, outputdir, overwrite=True):
#        _CreatorDispatcher.__init__(self, program, queue_options)
#
#        self._worker = program.worker_class()
#
#        if not os.path.isdir(outputdir):
#            raise ValueError('Output directory (%s) is not a directory' % outputdir)
#        self._outputdir = outputdir
#
#        self._overwrite = overwrite
#
#        self._close_event = threading.Event()
#        self._closed_event = threading.Event()
#
#    def run(self):
#        while not self._close_event.is_set():
#            try:
#                # Retrieve options
#                options = self._queue_options.get()
#
#                # Check if options already exists
#                xmlfilepath = os.path.join(self._outputdir, options.name + ".xml")
#                if os.path.exists(xmlfilepath) and not self._overwrite:
#                    logging.info('Skipping %s as options already exists', options.name)
#                    self._queue_options.task_done()
#                    continue
#
#                # Run
#                logging.debug('Running program specific worker')
#                self._worker.reset()
#                self._worker.create(options, self._outputdir)
#                logging.debug('End program specific worker')
#
#                self._queue_options.task_done()
#            except Exception:
#                self.stop()
#                self._queue_options.raise_exception()
#
#        self._closed_event.set()
#
#    def stop(self):
#        self._worker.stop()
#
#    def close(self):
#        if not self.is_alive():
#            return
#        self._worker.stop()
#        self._close_event.set()
#        self._closed_event.wait()
#
#    def report(self):
#        return self._worker.report()
#
#class LocalCreator(_Creator):
#
#    def __init__(self, program, outputdir, overwrite=True, nbprocesses=1):
#        """
#        Creates a new creator to create simulation files of several simulations.
#
#        Use :meth:`put` to add simulation to the creation list and then use the
#        method :meth:`start` to start the creation.
#        The method :meth:`join` before closing an application to ensure that
#        all simulations were created and all workers are stopped.
#
#        :arg program: program used to run the simulations
#
#        :arg outputdir: output directory for the simulation files.
#            The directory must exists.
#
#        :arg overwrite: whether to overwrite already existing simulation file(s)
#
#        :arg nbprocesses: number of processes/threads to use (default: 1)
#        """
#        _Creator.__init__(self, program)
#
#        if nbprocesses < 1:
#            raise ValueError("Number of processes must be greater or equal to 1.")
#
#        if not os.path.isdir(outputdir):
#            raise ValueError('Output directory (%s) is not a directory' % outputdir)
#
#        self._dispatchers = []
#        for _ in range(nbprocesses):
#            dispatcher = \
#                _LocalCreatorDispatcher(program, self._queue_options,
#                                        outputdir, overwrite)
#            self._dispatchers.append(dispatcher)
#
#    def start(self):
#        if not self._dispatchers:
#            raise RuntimeError("Runner is closed")
#
#        for dispatcher in self._dispatchers:
#            if not dispatcher.is_alive():
#                dispatcher.start()
#                logging.debug('Started dispatcher: %s', dispatcher.name)
#
#        logging.debug('Runner started')
#
#    def stop(self):
#        for dispatcher in self._dispatchers:
#            dispatcher.stop()
#        logging.debug('Runner stopped')
#
#    def close(self):
#        for dispatcher in self._dispatchers:
#            dispatcher.close()
#        self._dispatchers = []
#        logging.debug('Runner closed')
#
#    def report(self):
#        completed, progress, status = _Creator.report(self)
#
#        for dispatcher in self._dispatchers:
#            progress, status = dispatcher.report()
#            if progress > 0.0 and progress < 1.0: # active worker
#                return completed, progress, status
#
#        return completed, progress, status


