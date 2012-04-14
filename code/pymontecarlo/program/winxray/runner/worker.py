#!/usr/bin/env python
"""
================================================================================
:mod:`worker` -- WinX-Ray worker
================================================================================

.. module:: worker
   :synopsis: WinX-Ray 2 worker

.. inheritance-diagram:: pymontecarlo.runner.winxray.worker

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
from zipfile import ZipFile

# Third party modules.

# Local modules.
from pymontecarlo import settings
from pymontecarlo.runner.worker import SubprocessWorker as _Worker, InvalidPlatform
from pymontecarlo.runner.manager import WorkerManager

from pymontecarlo.program.winxray.input.converter import Converter
from pymontecarlo.program.winxray.io.exporter import Exporter
from pymontecarlo.program.winxray.io.importer import Importer


# Globals and constants variables.
from zipfile import ZIP_DEFLATED
from pymontecarlo.runner.manager import PLATFORM_WINDOWS

class Worker(_Worker):
    def __init__(self, queue_options, outputdir, workdir=None, overwrite=True):
        """
        Runner to run WinX-Ray simulation(s).
        """
        _Worker.__init__(self, queue_options, outputdir, workdir, overwrite)

        if platform.system() != PLATFORM_WINDOWS:
            raise InvalidPlatform, 'WinX-Ray can only be run on Windows'

        self._executable = settings.winxray.exe
        if not os.path.isfile(self._executable):
            raise IOError, 'WinX-Ray executable (%s) cannot be found' % self._executable
        logging.debug('WinX-Ray executable: %s', self._executable)

        self._executable_dir = os.path.dirname(self._executable)
        logging.debug('WinX-Ray directory: %s', self._executable_dir)

    def _create(self, options, dirpath):
        ops = copy.deepcopy(options)

        # Convert
        Converter().convert(ops)

        # Export
        filepath = self._get_filepath(ops, dirpath, 'wxc')
        if os.path.exists(filepath) and not self._overwrite:
            logging.info('Skipping %s as it already exists', filepath)
            return

        wxrops = Exporter().export(ops)

        if dirpath == self._workdir:
            wxrops.setResultsPath(self._get_dirpath(ops))

        # Save
        wxrops.write(filepath)
        logging.debug('Save wxc file: %s', filepath)

        return filepath

    def _run(self, options):
        wxcfilepath = self._create(options, self._workdir)
        if not wxcfilepath:
            return

        # Launch
        args = [self._executable, wxcfilepath]
        logging.debug('Launching %s', ' '.join(args))

        self._status = 'Running WinX-Ray'

        self._process = subprocess.Popen(args, stdout=subprocess.PIPE,
                                         cwd=self._executable_dir)
        self._process.wait()
        self._process = None

    def _save_results(self, options, zipfilepath):
        dirpath = self._get_dirpath(options)

        resultdirs = [name for name in os.listdir(dirpath) \
                      if os.path.isdir(os.path.join(dirpath, name)) ]
        resultdirs.sort()
        if not resultdirs:
            raise IOError, 'Cannot find results directories in %s' % dirpath

        # Import results to pyMonteCarlo
        path = os.path.join(dirpath, resultdirs[-1]) # Take last result folder
        results = Importer().import_from_dir(options, path)
        results.save(zipfilepath)

        # Append all WinXRay results in zip
        zip = ZipFile(zipfilepath, 'a', compression=ZIP_DEFLATED)

        for filename in os.listdir(path):
            filepath = os.path.join(path, filename)
            arcname = "raw/%s" % filename
            zip.write(filepath, arcname)

        zip.close()

WorkerManager.register('winxray', Worker, [PLATFORM_WINDOWS])
