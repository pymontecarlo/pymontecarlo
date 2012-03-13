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

# Third party modules.

# Local modules.

# Globals and constants variables.

class Runner(threading.Thread):
    def __init__(self, options, output, overwrite=True):
        """
        Base class for all runners. A runner is used to run a simulation with
        a given program.
        
        To start a runner, execute the method :meth:`start()`.
        The method :meth:`report()` can be used to retrieve the progress.
        
        :arg options: options of the simulation
        :type options: :class:`Options <pymontecarlo.input.base.options.Options>`
        
        :arg output: output directory or file of the simulation
        
        :arg overwrite: whether to overwrite results if they exist
            (default: ``True``)
        """
        threading.Thread.__init__(self)

        self._options = options
        self._output = os.path.abspath(output)
        self._overwrite = overwrite

    @property
    def options(self):
        """
        Options of the simulation.
        """
        return self._options

    @property
    def output(self):
        """
        Output directory or file (depending on the runner).
        """
        return self._output

    @property
    def overwrite(self):
        """
        Whether to overwrite results if they exist.
        """
        return self._overwrite

    def run(self):
        raise NotImplementedError

    def stop(self):
        """
        Stops the runner.
        """
        pass

    def report(self):
        """
        Returns a tuple of:
        
          * the progress of a simulation (between 0.0 and 1.0)
          * text indicating the status
        """
        return 0.0, ""
