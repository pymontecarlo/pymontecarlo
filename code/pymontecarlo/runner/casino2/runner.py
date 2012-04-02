#!/usr/bin/env python
"""
================================================================================
:mod:`runner` -- Casino 2 runner
================================================================================

.. module:: runner
   :synopsis: Casino 2 runner

.. inheritance-diagram:: pymontecarlo.runner.casino2.runner

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
from pymontecarlo.runner.base.runner import Runner as _Runner, InvalidPlatform
from pymontecarlo.runner.base.manager import RunnerManager

# Globals and constants variables.
from pymontecarlo.runner.base.manager import PLATFORM_WINDOWS

class Runner(_Runner):
    def __init__(self, options, outputdir, overwrite=True):
        """
        Runner to run Casino2 simulation(s).
        """
        _Runner.__init__(self, options, outputdir, overwrite)

        if platform.system() != PLATFORM_WINDOWS:
            raise InvalidPlatform, 'Casino 2 can only be run on Windows'

        self._executable = settings.casino2.exe
        if not os.path.exists(self._executable):
            raise IOError, 'Casino 2 executable (%s) cannot be found' % self._executable
        logging.debug('Casino 2 executable: %s', self._executable)

    def _reset(self):
        _Runner._reset(self)
        self._process = None

    def _create_sim(self, options):
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

    def _run_multiple(self):
        filepaths = []

        # Save all options
        for options in self._options:
            filepath = self._create_sim(options)
            if filepath:
                filepaths.append(filepath)

        # Exit if no options need to be run
        if not filepaths:
            return

        # Start Casino 2
        args = [self._executable]
        logging.debug('Launching %s', ' '.join(args))

        self._status = 'Running Casino 2'

        self._process = subprocess.Popen(args, stdout=subprocess.PIPE)

        while self._process.poll() == None:
            time.sleep(1)

            self._check_completed_simulations()
            if len(self._completed) == len(self._options):
                self._process.kill()
                break

        self._process = None

    def stop(self):
        _Runner.stop(self)
        if self._process is not None:
            self._process.kill()

    def _check_completed_simulations(self):
        self._completed = []

        for options in self._options:
            if os.path.exists(self._get_filepath(options, 'cas')):
                self._completed.append(options)

    def _get_results_single(self, options):
        filepath = self._get_filepath(options, 'cas')
        if not os.path.exists(filepath):
            raise IOError, 'Cannot find cas file: %s' % filepath

        with open(filepath, 'rb') as fp:
            results = Importer().import_from_cas(options, fp)

        return results

RunnerManager.register('casino', Runner, [PLATFORM_WINDOWS])
