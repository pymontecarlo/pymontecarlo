#!/usr/bin/env python
"""
================================================================================
:mod:`worker` -- WinX-Ray worker
================================================================================

.. module:: worker
   :synopsis: WinX-Ray 2 worker

.. inheritance-diagram:: pymontecarlo.program.winxray.runner.worker

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
from zipfile import ZipFile

# Third party modules.

# Local modules.
from pymontecarlo.settings import get_settings
from pymontecarlo.runner.worker import SubprocessWorker as _Worker

from pymontecarlo.program.winxray.input.converter import Converter
from pymontecarlo.program.winxray.input.exporter import Exporter
from pymontecarlo.program.winxray.output.importer import Importer


# Globals and constants variables.
from zipfile import ZIP_DEFLATED

class Worker(_Worker):
    def __init__(self, queue_options, outputdir, workdir=None, overwrite=True):
        """
        Runner to run WinX-Ray simulation(s).
        """
        _Worker.__init__(self, queue_options, outputdir, workdir, overwrite)

        self._executable = get_settings().winxray.exe
        if not os.path.isfile(self._executable):
            raise IOError, 'WinX-Ray executable (%s) cannot be found' % self._executable
        logging.debug('WinX-Ray executable: %s', self._executable)

        self._executable_dir = os.path.dirname(self._executable)
        logging.debug('WinX-Ray directory: %s', self._executable_dir)

    def _create(self, options, dirpath):
        # Convert
        Converter().convert(options)

        # Export
        wxrops = Exporter().export(options)

        if dirpath == self._workdir:
            wxrops.setResultsPath(self._get_dirpath(options))

        # Save
        filepath = self._get_filepath(options, dirpath, 'wxc')
        wxrops.write(filepath)
        logging.debug('Save wxc file: %s', filepath)

        return filepath

    def _run(self, options):
        wxcfilepath = self._create(options, self._workdir)

        # Launch
        args = [self._executable, wxcfilepath]
        logging.debug('Launching %s', ' '.join(args))

        self._status = 'Running WinX-Ray'

        self._process = subprocess.Popen(args, stdout=subprocess.PIPE,
                                         cwd=self._executable_dir)
        self._process.wait()
        self._process = None

        logging.debug('WinX-Ray ended')

    def _save_results(self, options, h5filepath):
        dirpath = self._get_dirpath(options)

        resultdirs = [name for name in os.listdir(dirpath) \
                      if os.path.isdir(os.path.join(dirpath, name)) ]
        resultdirs.sort()
        if not resultdirs:
            raise IOError, 'Cannot find results directories in %s' % dirpath

        # Import results to pyMonteCarlo
        logging.debug('Importing results from WinXRay')
        path = os.path.join(dirpath, resultdirs[-1]) # Take last result folder
        results = Importer().import_from_dir(options, path)
        results.save(h5filepath)

        # Create ZIP with all WinXRay results
        zipfilepath = os.path.splitext(h5filepath)[0] + '_raw.zip'
        with ZipFile(zipfilepath, 'w', compression=ZIP_DEFLATED) as zipfile:
            for filename in os.listdir(dirpath):
                filepath = os.path.join(dirpath, filename)
                zipfile.write(filepath)
