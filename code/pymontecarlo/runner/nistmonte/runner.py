#!/usr/bin/env python
"""
================================================================================
:mod:`runner` -- NISTMonte runner
================================================================================

.. module:: runner
   :synopsis: NISTMonte runner

.. inheritance-diagram:: pymontecarlo.runner.nistmonte.runner

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

# Third party modules.

# Local modules.
from pymontecarlo import settings
from pymontecarlo.input.nistmonte.converter import Converter
from pymontecarlo.result.base.results import Results
from pymontecarlo.runner.base.runner import Runner as _Runner
from pymontecarlo.runner.base.manager import RunnerManager

# Globals and constants variables.

class Runner(_Runner):
    def __init__(self, options, outputdir, overwrite=True):
        """
        Runner to run NISTMonte simulation(s).
        """
        _Runner.__init__(self, options, outputdir, overwrite)

        self._java_exec = settings.nistmonte.java
        if not os.path.exists(self._java_exec):
            raise IOError, 'Java executable (%s) cannot be found' % self._java_exec
        logging.debug('Java executable: %s', self._java_exec)

        self._jar_path = settings.nistmonte.jar
        if not os.path.exists(self._jar_path):
            raise IOError, 'pyMonteCarlo jar (%s) cannot be found' % self._jar_path
        logging.debug('pyMonteCarlo jar path: %s', self._jar_path)

    def _reset(self):
        _Runner._reset(self)
        self._process = None

    def _save_options(self, options):
        ops = copy.deepcopy(options)

        # Convert
        Converter().convert(ops)

        # Save
        filepath = self._get_filepath(ops, 'xml')
        if os.path.exists(filepath) and not self.overwrite:
            logging.info('Skipping %s as it already exists', filepath)
            return

        ops.save(filepath)
        logging.debug('Save options to: %s', filepath)

        return filepath

    def _run_single(self, options):
        options_filepath = self._save_options(options)
        if not options_filepath:
            return

        args = [self._java_exec]
        args += ['-jar', self._jar_path]
        args += ['-o', self._outputdir]
        args += [options_filepath]
        logging.debug('Launching %s', ' '.join(args))

        self._process = subprocess.Popen(args, stdout=subprocess.PIPE)

        for line in iter(self._process.stdout.readline, ""):
            infos = line.split('\t')
            if len(infos) == 2:
                self._progress = float(infos[0])
                self._status = infos[1].strip()

        self._process.wait()
        self._process = None

    def stop(self):
        _Runner.stop(self)
        if self._process is not None:
            self._process.kill()

    def _get_results_single(self, options):
        filepath = self._get_filepath(options, 'zip')
        if not os.path.exists(filepath):
            raise IOError, 'Cannot find results zip: %s' % filepath

        return Results.load(filepath, options)

RunnerManager.register('NISTMonte', Runner)
