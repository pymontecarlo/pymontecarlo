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
from pymontecarlo.runner.base.runner import Runner as _Runner
from pymontecarlo.runner.base.manager import RunnerManager

# Globals and constants variables.

class Runner(_Runner):
    def __init__(self, options, output, overwrite=True):
        """
        Runner to run a NISTMonte simulation.
        
        :arg options: options of the simulation
        :type options: :class:`Options <pymontecarlo.input.base.options.Options>`
        
        :arg output: output directory of the simulation
        """
        _Runner.__init__(self, options, output, overwrite)

        if not os.path.isdir(output):
            raise ValueError, 'Output (%s) is not a directory' % output

        self._java_exec = settings.nistmonte.java
        if not os.path.exists(self._java_exec):
            raise IOError, 'Java executable (%s) cannot be found' % self._java_exec
        logging.debug('Java executable: %s', self._java_exec)

        self._jar_path = settings.nistmonte.jar
        if not os.path.exists(self._jar_path):
            raise IOError, 'pyMonteCarlo jar (%s) cannot be found' % self._jar_path
        logging.debug('pyMonteCarlo jar path: %s', self._jar_path)

        self._process = None
        self._progress = 0.0
        self._status = ''

    def _save_options(self):
        ops = copy.deepcopy(self.options)

        # Convert
        Converter().convert(ops)

        # Save
        filepath = os.path.join(self.output, ops.name + ".xml")
        if os.path.exists(filepath) and not self.overwrite:
            return

        ops.save(filepath)
        logging.debug('Save options to: %s', filepath)

        return filepath

    def run(self):
        options_filepath = self._save_options()
        if not options_filepath:
            return

        args = [self._java_exec]
        args += ['-jar', self._jar_path]
        args += ['-o', self.output]
        args += [options_filepath]
        logging.debug('Launching %s', ' '.join(args))

        self._progress = 0.0
        self._status = 'Starting'

        self._process = subprocess.Popen(args, stdout=subprocess.PIPE)
        for line in iter(self._process.stdout.readline, ""):
            infos = line.split('\t')
            if len(infos) == 2:
                self._progress = float(infos[0])
                self._status = infos[1].strip()

        self._process = None
        self._progress = 1.0
        self._status = 'Finished'

    def stop(self):
        if self._process is not None:
            self._process.kill()
            self._status = 'Stopped'

    def report(self):
        return self._progress, self._status

RunnerManager.register('NISTMonte', Runner)
