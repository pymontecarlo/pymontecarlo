#!/usr/bin/env python
"""
================================================================================
:mod:`worker` -- PENEPMA worker 
================================================================================

.. module:: worker
   :synopsis: PENEPMA worker

.. inheritance-diagram:: pymontecarlo.program.penepma.runner.worker

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
from zipfile import ZipFile

# Third party modules.

# Local modules.
from pymontecarlo import get_settings
from pymontecarlo.input.limit import TimeLimit, ShowersLimit, UncertaintyLimit
from pymontecarlo.runner.worker import SubprocessWorker as _Worker

from pymontecarlo.program.penepma.input.converter import Converter
from pymontecarlo.program.penepma.io.exporter import Exporter
from pymontecarlo.program.penepma.io.importer import Importer

# Globals and constants variables.
from zipfile import ZIP_DEFLATED

class Worker(_Worker):
    def __init__(self, queue_options, outputdir, workdir=None, overwrite=True):
        """
        Runner to run PENEPMA simulation(s).
        """
        _Worker.__init__(self, queue_options, outputdir, workdir, overwrite)

        self._executable = get_settings().penelope.penepma_exe
        if not os.path.isfile(self._executable):
            raise IOError, 'PENEPMA executable (%s) cannot be found' % self._executable
        logging.debug('PENEPMA executable: %s', self._executable)

    def _create(self, options, dirpath):
        ops = copy.deepcopy(options)

        # Convert
        Converter().convert(ops)

        # Export
        dirpath = self._get_dirpath(ops)
        if os.listdir(dirpath): # not empty
            logging.info("Simulation directory (%s) is not empty. It will be empty.", dirpath)
            shutil.rmtree(dirpath)
            os.makedirs(dirpath)

        # Create .in, .geo and all .mat
        infilepath = Exporter().export(ops, dirpath)

        # Save
        logging.debug('Save in file: %s', infilepath)

        return infilepath

    def _run(self, options):
        infilepath = self._create(options, self._workdir)

        # Extract limit
        limit = options.limits.find(ShowersLimit)
        showers_limit = limit.showers if limit else 1e38

        limit = options.limits.find(TimeLimit)
        time_limit = limit.time_s if limit else 1e38

        limit = options.limits.find(UncertaintyLimit)
        uncertainty_limit = limit.uncertainty if limit else float('inf')

        # Launch
        args = [self._executable]
        stdin = open(infilepath, 'r')
        logging.debug('Launching %s', ' '.join(args))

        self._status = 'Running PENEPMA'
        self._progress = 0.001 # Ensure that the simulation has started

        self._process = \
            subprocess.Popen(args, stdin=stdin, stdout=subprocess.PIPE,
                             cwd=os.path.dirname(infilepath))

        for line in iter(self._process.stdout.readline, ""):
            infos = line.split(',')
            if len(infos) == 1:
                self._status = infos[0].strip()
            elif len(infos) == 4:
                progress_showers = float(infos[0]) / showers_limit
                progress_time = float(infos[1]) / time_limit
                progress_uncertainty = float(infos[2]) / uncertainty_limit
                self._progress = max(0.001, progress_showers, progress_time,
                                     progress_uncertainty)
                self._status = 'Running'

        self._process.wait()
        retcode = self._process.returncode

        self._process = None

        if retcode != 0:
            raise RuntimeError, "An error occurred during the simulation"

    def _save_results(self, options, zipfilepath):
        dirpath = self._get_dirpath(options)

        # Import results to pyMonteCarlo
        results = Importer().import_from_dir(options, dirpath)
        results.save(zipfilepath)

        # Append all PENEPMA results in zip
        zip = ZipFile(zipfilepath, 'a', compression=ZIP_DEFLATED)

        for filename in os.listdir(dirpath):
            filepath = os.path.join(dirpath, filename)
            arcname = "raw/%s" % filename
            zip.write(filepath, arcname)

        zip.close()

