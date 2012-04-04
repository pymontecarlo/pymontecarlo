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
import subprocess
import logging
import platform
import time

# Third party modules.

# Local modules.
from pymontecarlo import settings
from pymontecarlo.input.casino2.converter import Converter
from pymontecarlo.io.casino2.exporter import Exporter
from pymontecarlo.io.casino2.importer import Importer
from pymontecarlo.runner.base.worker import SubprocessWorker as _Worker, InvalidPlatform
from pymontecarlo.runner.base.manager import WorkerManager

# Globals and constants variables.
from pymontecarlo.runner.base.manager import PLATFORM_WINDOWS

class Worker(_Worker):
    def __init__(self, queue_options, queue_results, outputdir, overwrite=True):
        """
        Runner to run Casino2 simulation(s).
        """
        _Worker.__init__(self, queue_options, queue_results,
                         outputdir, overwrite=overwrite)

        if platform.system() != PLATFORM_WINDOWS:
            raise InvalidPlatform, 'Casino 2 can only be run on Windows'

        self._executable = settings.casino2.exe
        if not os.path.exists(self._executable):
            raise IOError, 'Casino 2 executable (%s) cannot be found' % self._executable
        logging.debug('Casino 2 executable: %s', self._executable)

    def _create(self, options):
        ops = copy.deepcopy(options)

        # Convert
        Converter().convert(ops)

        # Export
        simfilepath = self._get_filepath(ops, 'sim')
        if os.path.exists(simfilepath) and not self._overwrite:
            logging.info('Skipping %s as it already exists', simfilepath)
            return

        simfile = Exporter().export(ops)

        # Save
        simfile.write(simfilepath)
        logging.debug('Save sim file: %s', simfilepath)

        # Remove previous .cas file
        casfilepath = os.path.splitext(simfilepath)[0] + ".cas"
        if os.path.exists(casfilepath):
            os.remove(casfilepath)

        return simfilepath

    def _run(self, options):
        simfilepath = self._create(options)
        if not simfilepath:
            return # Exit if no options need to be run

        casfilepath = self._get_filepath(options, 'cas')

        # Start Casino 2
        args = [self._executable]
        logging.debug('Launching %s', ' '.join(args))

        self._status = 'Running Casino 2'

        self._process = subprocess.Popen(args, stdout=subprocess.PIPE)

        while self._process.poll() == None:
            time.sleep(1)

            if os.path.exists(casfilepath):
                self._process.kill()
                break

        self._process = None

    def _get_results(self, options):
        filepath = self._get_filepath(options, 'cas')
        if not os.path.exists(filepath):
            raise IOError, 'Cannot find cas file: %s' % filepath

        with open(filepath, 'rb') as fp:
            results = Importer().import_from_cas(options, fp)

        return results

WorkerManager.register('casino2', Worker, [PLATFORM_WINDOWS])
