#!/usr/bin/env python
"""
================================================================================
:mod:`worker` -- Casino 2 worker
================================================================================

.. module:: worker
   :synopsis: Casino 2 worker

.. inheritance-diagram:: pymontecarlo.program.casino2.runner.worker

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2012 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import os
import logging

# Third party modules.

# Local modules.
from pymontecarlo.settings import get_settings
from pymontecarlo.program.worker import Worker as _Worker

# Globals and constants variables.

class Worker(_Worker):
    def __init__(self, program):
        """
        Runner to run Casino2 simulation(s).
        """
        _Worker.__init__(self, program)

        self._executable = get_settings().casino2.exe
        if not os.path.isfile(self._executable):
            raise IOError('Casino 2 executable (%s) cannot be found' % self._executable)
        logging.debug('Casino 2 executable: %s', self._executable)

    def run(self, options, outputdir, workdir, *args, **kwargs):
        raise NotImplementedError("Simulations with Casino2 cannot be directly run. " + \
            "Please use the create method to create the .sim files and run them in Casino 2.")
