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
from pymontecarlo.settings import get_settings
from pymontecarlo.input.limit import ShowersLimit
from pymontecarlo.runner.worker import SubprocessWorker as _Worker

# Globals and constants variables.
from zipfile import ZIP_DEFLATED

class Worker(_Worker):

    def __init__(self, program):
        """
        Runner to run PENSHOWER simulation(s).
        """
        _Worker.__init__(self, program)

        self._executable = get_settings().penshower.exe
        if not os.path.isfile(self._executable):
            raise IOError, 'PENSHOWER executable (%s) cannot be found' % self._executable
        logging.debug('PENSHOWER executable: %s', self._executable)

    def create(self, options, outputdir, *args, **kwargs):
        # Create directory if needed
        if kwargs.get('createdir', True):
            simdir = os.path.join(outputdir, options.name)
            if os.path.exists(simdir):
                logging.info("Simulation directory (%s) exists. It will be empty.", simdir)
                shutil.rmtree(simdir, ignore_errors=True)
            os.makedirs(simdir)
        else:
            simdir = outputdir

        return _Worker.create(self, options, outputdir, *args, **kwargs)

    def run(self, options, outputdir, workdir, *args, **kwargs):
        infilepath = self.create(options, workdir, createdir=False)

        # Extract limit
        limits = list(options.limits.iterclass(ShowersLimit))
        showers_limit = limits[0].showers if limits else 1e38

        # Launch
        args = [self._executable]
        stdin = open(infilepath, 'r')
        logging.debug('Launching %s', ' '.join(args))

        self._status = 'Running PENSHOWER'
        self._progress = 0.001 # Ensure that the simulation has started

        self._process = \
            subprocess.Popen(args, stdin=stdin, stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT, cwd=workdir)

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

        return self._extract_results(options, outputdir, workdir)

    def _extract_results(self, options, outputdir, workdir):
        # Import results to pyMonteCarlo
        self._status = 'Importing results'
        results = self._importer.import_(options, workdir)

        # Create ZIP with all PENSHOWER results
        zipfilepath = os.path.join(outputdir, options.name + '.zip')
        with ZipFile(zipfilepath, 'w', compression=ZIP_DEFLATED) as zipfile:
            for filename in os.listdir(workdir):
                if filename == 'pe-trajectories.dat':
                    continue
                filepath = os.path.join(workdir, filename)
                zipfile.write(filepath, filename)

        return results
