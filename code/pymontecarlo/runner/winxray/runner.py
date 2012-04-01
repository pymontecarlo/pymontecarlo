#!/usr/bin/env python
"""
================================================================================
:mod:`runner` -- WinX-Ray runner
================================================================================

.. module:: runner
   :synopsis: WinX-Ray 2 runner

.. inheritance-diagram:: pymontecarlo.runner.winxray.runner

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
from pymontecarlo.input.winxray.converter import Converter
from pymontecarlo.io.winxray.exporter import Exporter
from pymontecarlo.io.winxray.importer import Importer
from pymontecarlo.runner.base.runner import Runner as _Runner, InvalidPlatform
from pymontecarlo.runner.base.manager import RunnerManager

# Globals and constants variables.


class Runner(_Runner):
    def __init__(self, options, outputdir, overwrite=True):
        """
        Runner to run WinX-Ray simulation(s).
        """
        _Runner.__init__(self, options, outputdir, overwrite)

        if platform.system() != 'Windows':
            raise InvalidPlatform, 'WinX-Ray can only be run on Windows'

        self._executable = settings.winxray.exe
        if not os.path.exists(self._executable):
            raise IOError, 'WinX-Ray executable (%s) cannot be found' % self._executable
        logging.debug('WinX-Ray executable: %s', self._executable)

    def _reset(self):
        _Runner._reset(self)
        self._process = None

    def _create_sim(self, options):
        ops = copy.deepcopy(options)

        # Convert
        Converter().convert(ops)

        # Export
        filepath = self._get_filepath(ops, 'wxc')
        if os.path.exists(filepath) and not self.overwrite:
            logging.info('Skipping %s as it already exists', filepath)
            return

        wxrops = Exporter().export(ops)
        wxrops.setResultsPath(self._get_dirpath(ops))

        # Save
        wxrops.write(filepath)
        logging.debug('Save wxc file: %s', filepath)

        return filepath

    def _run_single(self, options):
        wxc_filepath = self._create_sim(options)
        if not wxc_filepath:
            return

        args = [self._executable, wxc_filepath]
        logging.debug('Launching %s', ' '.join(args))

        self._status = 'Running WinX-Ray'

        self._process = subprocess.Popen(args, stdout=subprocess.PIPE)
        self._process.wait()
        self._process = None

    def stop(self):
        _Runner.stop(self)
        if self._process is not None:
            self._process.kill()

    def _get_results_single(self, options):
        dirpath = self._get_dirpath(options)

        resultdirs = sorted(os.listdir(dirpath))
        if not resultdirs:
            raise IOError, 'Cannot find results directories in %s' % dirpath

        path = os.path.join(dirpath, resultdirs[-1]) # Take last result folder
        results = Importer().import_from_dir(options, path)

        return results

    def _get_dirpath(self, options):
        dirpath = os.path.join(self._outputdir, options.name)
        if not os.path.exists(dirpath):
            os.makedirs(dirpath)

        return dirpath

RunnerManager.register('WinX-Ray', Runner)
