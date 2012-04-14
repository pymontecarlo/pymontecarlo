#!/usr/bin/env python
"""
================================================================================
:mod:`worker` -- NISTMonte worker
================================================================================

.. module:: worker
   :synopsis: NISTMonte worker

.. inheritance-diagram:: pymontecarlo.runner.nistmonte.worker

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
import shutil

# Third party modules.

# Local modules.
from pymontecarlo import settings
from pymontecarlo.program.nistmonte.input.converter import Converter
from pymontecarlo.runner.worker import SubprocessWorker as _Worker
from pymontecarlo.runner.manager import WorkerManager

# Globals and constants variables.
from pymontecarlo.runner.manager import ALL_PLATFORMS

class Worker(_Worker):
    def __init__(self, queue_options, outputdir, workdir=None, overwrite=True):
        """
        Runner to run NISTMonte simulation(s).
        """
        _Worker.__init__(self, queue_options, outputdir, workdir, overwrite)

        self._java_exec = settings.nistmonte.java
        if not os.path.isfile(self._java_exec):
            raise IOError, 'Java executable (%s) cannot be found' % self._java_exec
        logging.debug('Java executable: %s', self._java_exec)

        self._jar_path = settings.nistmonte.jar
        if not os.path.isfile(self._jar_path):
            raise IOError, 'pyMonteCarlo jar (%s) cannot be found' % self._jar_path
        logging.debug('pyMonteCarlo jar path: %s', self._jar_path)

    def _create(self, options, dirpath):
        ops = copy.deepcopy(options)

        # Convert
        Converter().convert(ops)

        # Save
        filepath = self._get_filepath(ops, dirpath, 'xml')
        if os.path.exists(filepath) and not self._overwrite:
            logging.info('Skipping %s as it already exists', filepath)
            return

        ops.save(filepath)
        logging.debug('Save options to: %s', filepath)

        return filepath

    def _run(self, options):
        xmlfilepath = self._create(options, self._workdir)
        if not xmlfilepath:
            return # Exit if no options need to be run

        args = [self._java_exec]
        args += ['-jar', self._jar_path]
        args += ['-o', self._workdir]
        args += [xmlfilepath]
        logging.debug('Launching %s', ' '.join(args))

        self._process = subprocess.Popen(args, stdout=subprocess.PIPE)

        for line in iter(self._process.stdout.readline, ""):
            infos = line.split('\t')
            if len(infos) == 2:
                self._progress = float(infos[0])
                self._status = infos[1].strip()

        self._process.wait()
        retcode = self._process.returncode

        self._process = None

        if retcode != 0:
            raise RuntimeError, "An error occured during the simulation"

    def _save_results(self, options, zipfilepath):
        work_zipfilepath = self._get_filepath(options, self._workdir, 'zip')
        shutil.copy(work_zipfilepath, zipfilepath)

WorkerManager.register('nistmonte', Worker, ALL_PLATFORMS)
