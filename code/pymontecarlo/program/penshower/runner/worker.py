#!/usr/bin/env python
"""
================================================================================
:mod:`worker` -- PENSHOWER worker 
================================================================================

.. module:: worker
   :synopsis: PENSHOWER worker

.. inheritance-diagram:: pymontecarlo.program.penshower.runner.worker

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2012 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import os
import subprocess
import logging
import shutil
from zipfile import ZipFile

# Third party modules.

# Local modules.
from pymontecarlo import get_settings
from pymontecarlo.input.limit import ShowersLimit
from pymontecarlo.runner.worker import SubprocessWorker as _Worker

from pymontecarlo.program.penshower.input.converter import Converter
from pymontecarlo.program.penshower.io.exporter import Exporter
from pymontecarlo.program.penshower.io.importer import Importer

# Globals and constants variables.
from zipfile import ZIP_DEFLATED

class Worker(_Worker):
    def __init__(self, queue_options, outputdir, workdir=None, overwrite=True):
        """
        Runner to run PENSHOWER simulation(s).
        """
        _Worker.__init__(self, queue_options, outputdir, workdir, overwrite)

        self._executable = get_settings().penshower.exe
        if not os.path.isfile(self._executable):
            raise IOError, 'PENSHOWER executable (%s) cannot be found' % self._executable
        logging.debug('PENSHOWER executable: %s', self._executable)

    def _create(self, options, dirpath):
        # Convert
        Converter().convert(options)

        # Export
        dirpath = self._get_dirpath(options)
        if os.listdir(dirpath): # not empty
            logging.info("Simulation directory (%s) is not empty. It will be empty.", dirpath)
            shutil.rmtree(dirpath)
            os.makedirs(dirpath)

        # Create .in, .geo and all .mat
        infilepath = Exporter().export(options, dirpath)

        # Save
        logging.debug('Save in file: %s', infilepath)

        return infilepath

    def _run(self, options):
        infilepath = self._create(options, self._workdir)

        # Extract limit
        limit = options.limits.find(ShowersLimit)
        showers_limit = limit.showers if limit else 1e38

        # Launch
        args = [self._executable]
        stdin = open(infilepath, 'r')
        logging.debug('Launching %s', ' '.join(args))

        self._status = 'Running PENSHOWER'
        self._progress = 0.001 # Ensure that the simulation has started

        self._process = \
            subprocess.Popen(args, stdin=stdin, stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT,
                             cwd=os.path.dirname(infilepath))

        for line in iter(self._process.stdout.readline, ""):
            infos = line.split(',')
            if len(infos) == 1:
                self._status = infos[0].strip()
                if self._status.startswith('STOP'):
                    raise RuntimeError, "The following error occurred during the simulation: %s" % self._status
            elif len(infos) == 2:
                self._progress = max(0.001, float(infos[0]) / showers_limit)
                self._status = 'Running'

        self._process.wait()
        retcode = self._process.returncode

        self._process = None

        if retcode != 0:
            raise RuntimeError, "An error occurred during the simulation"

    def _save_results(self, options, zipfilepath):
        dirpath = self._get_dirpath(options)

        # Import results to pyMonteCarlo
        self._status = 'Importing results'
        results = Importer().import_from_dir(options, dirpath)
        results.save(zipfilepath)

        # Append all PENSHOWER results in zip, except pe-trajectories.dat
        zip = ZipFile(zipfilepath, 'a', compression=ZIP_DEFLATED)

        for filename in os.listdir(dirpath):
            if filename == 'pe-trajectories.dat':
                continue
            filepath = os.path.join(dirpath, filename)
            arcname = "raw/%s" % filename
            zip.write(filepath, arcname)

        zip.close()

