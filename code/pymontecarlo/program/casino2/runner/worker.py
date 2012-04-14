#!/usr/bin/env python
"""
================================================================================
:mod:`worker` -- Casino 2 worker
================================================================================

.. module:: worker
   :synopsis: Casino 2 worker

.. inheritance-diagram:: pymontecarlo.runner.casino2.worker

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
import platform

# Third party modules.

# Local modules.
from pymontecarlo import settings
from pymontecarlo.program.casino2.input.converter import Converter
from pymontecarlo.program.casino2.io.exporter import Exporter
from pymontecarlo.runner.worker import Worker as _Worker, InvalidPlatform
from pymontecarlo.runner.manager import WorkerManager

# Globals and constants variables.
from pymontecarlo.runner.manager import PLATFORM_WINDOWS

class Worker(_Worker):
    def __init__(self, queue_options, outputdir, workdir=None, overwrite=True):
        """
        Runner to run Casino2 simulation(s).
        """
        _Worker.__init__(self, queue_options, outputdir, workdir, overwrite)

        if platform.system() != PLATFORM_WINDOWS:
            raise InvalidPlatform, 'Casino 2 can only be run on Windows'

        self._executable = settings.casino2.exe
        if not os.path.isfile(self._executable):
            raise IOError, 'Casino 2 executable (%s) cannot be found' % self._executable
        logging.debug('Casino 2 executable: %s', self._executable)

    def _create(self, options, dirpath):
        ops = copy.deepcopy(options)

        # Convert
        Converter().convert(ops)

        # Export
        simfilepath = self._get_filepath(ops, dirpath, 'sim')
        if os.path.exists(simfilepath) and not self._overwrite:
            logging.info('Skipping %s as it already exists', simfilepath)
            return

        simfile = Exporter().export(ops)

        # Save
        simfile.write(simfilepath)
        logging.debug('Save sim file: %s', simfilepath)

        return simfilepath

    def _run(self, options):
        raise NotImplementedError, "Simulations with Casino2 cannot be directly run. " + \
            "Please use the create method to create the .sim files and run them in Casino 2."

WorkerManager.register('casino2', Worker, [PLATFORM_WINDOWS])
