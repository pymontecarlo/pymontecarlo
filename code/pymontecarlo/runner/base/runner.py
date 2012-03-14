#!/usr/bin/env python
"""
================================================================================
:mod:`runner` -- Base runner
================================================================================

.. module:: runner
   :synopsis: Base runner

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
import threading
import collections

# Third party modules.

# Local modules.

# Globals and constants variables.

class InvalidPlatform(Exception):
    pass

class Runner(threading.Thread):
    def __init__(self, options, outputdir, overwrite=True):
        """
        Base class for all runners. A runner is used to run one **or many** 
        simulations with a given program.
        
        To start a runner, execute the method :meth:`start()`.
        The method :meth:`report()` can be used to retrieve the progress.
        
        :arg options: options of the simulation or :class:`list` of options of
            several simulations. The order of the simulations is preserved.
        :type options: :class:`Options <pymontecarlo.input.base.options.Options>`
            or :class:`list` of :class:`Options <pymontecarlo.input.base.options.Options>`
        
        :arg outputdir: output directory of the simulation(s).
            The directory must exists.
        
        :arg overwrite: whether to overwrite results if they exist
            (default: ``True``)
        """
        threading.Thread.__init__(self)

        if not isinstance(options, collections.Iterable):
            options = [options]
        self._options = options

        if not os.path.isdir(outputdir):
            raise ValueError, 'Output (%s) is not a directory' % outputdir
        self._outputdir = os.path.abspath(outputdir)

        self._overwrite = overwrite

        self._reset()

    def _reset(self):
        self._progress = 0.0
        self._status = ''
        self._continue = True
        self._completed = []

    def run(self):
        self._reset()
        self._run_multiple()
        self._status = 'Completed'

    def _run_multiple(self):
        for options in self._options:
            if not self._continue:
                break

            self._progress = 0.0
            self._status = 'Starting'

            self._run_single_options(options)

            self._progress = 1.0
            self._status = 'Finished'
            self._completed.append(options)

    def _run_single(self, options):
        raise NotImplementedError

    def stop(self):
        """
        Stops all simulations.
        """
        self._status = 'Stopped'
        self._continue = False # Prevent run() from continuing

    def report(self):
        """
        Returns a tuple of:
        
          * counter of which simulation is running from the list of simulation.
              If only one simulation was specified, this counter is always equal
              to 1.
          * the progress of the current running simulation (between 0.0 and 1.0)
          * text indicating the status of the current running simulation
        """
        return len(self._completed) + 1, self._progress, self._status

    def get_results(self):
        """
        Returns the results of the run. 
        
        .. note:: 
        
            Note that only the results of the completed simulations are returned.
            To be sure to get all the results, called :meth:`join()` before
            this method
            
        :return: results of each completed simulation
        :rtype: :class:`list` of :class:`Results <pymontecarlo.result.base.results.Results>`
        """
        results = []

        for options in self._completed:
            results.append(self._get_results_single(options))

        return results

    def _get_results_single(self, options):
        raise NotImplementedError

    def _get_filepath(self, options, ext='xml'):
        return os.path.join(self._outputdir, options.name + "." + ext)
