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

# Third party modules.

# Local modules.
from pymontecarlo import settings
from pymontecarlo.input.casino2.converter import Converter
from pymontecarlo.io.casino2.exporter import Exporter
from pymontecarlo.io.casino2.importer import Importer
from pymontecarlo.runner.base.runner import Runner as _Runner, InvalidPlatform
from pymontecarlo.runner.base.manager import RunnerManager

# Globals and constants variables.


class Runner(_Runner):
    def __init__(self, options, outputdir, overwrite=True):
        """
        Runner to run Casino2 simulation(s).
        """
        _Runner.__init__(self, options, outputdir, overwrite)

        if platform.system() != 'Windows':
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
        filepath = self._get_filepath(ops, 'sim')
        if os.path.exists(filepath) and not self.overwrite:
            logging.info('Skipping %s as it already exists', filepath)
            return

        casfile = Exporter().export(ops)

        # Save
        casfile.write(filepath)
        logging.debug('Save cas file: %s', filepath)

        return filepath

    def _run_multiple(self):
        filepaths = []

        # Save all options
        for options in self._options:
            filepath = self._save_options(options)
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
        self._process.wait()

    def stop(self):
        _Runner.stop(self)
        if self._process is not None:
            self._process.kill()

    def _check_completed_simulations(self):
        self._completed = []

        for options in self._options:
            if os.path.exists(self._get_filepath(options, 'cas')):
                self._completed.append(options)

    def report(self):
        self._check_completed_simulations()
        return _Runner.report(self)

    def get_results(self):
        self._check_completed_simulations()
        return _Runner.get_results(self)

    def _get_results_single(self, options):
        filepath = self._get_filepath(options, 'cas')
        if not os.path.exists(filepath):
            raise IOError, 'Cannot find cas file: %s' % filepath

        with open(filepath, 'r') as fp:
            results = Importer().import_from_cas(options, fp)

        return results

RunnerManager.register('Casino2', Runner)
