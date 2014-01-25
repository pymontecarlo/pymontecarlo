#!/usr/bin/env python
"""
================================================================================
:mod:`worker` -- Casino 3 worker
================================================================================

.. module:: worker
   :synopsis: Casino 3 worker

.. inheritance-diagram:: pymontecarlo.program.casino3.runner.worker

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
from pymontecarlo.program.worker import SubprocessWorker as _Worker

from pymontecarlo.program.casino3.converter import Converter
#from pymontecarlo.program.casino3.io.exporter import Exporter
from pymontecarlo.program.casino3.importer import Importer


# Globals and constants variables.
from zipfile import ZIP_DEFLATED

class Worker(_Worker):
    def __init__(self, queue_options, outputdir, workdir=None, overwrite=True):
        """
        Runner to run Casino 3 simulation(s).
        """
        _Worker.__init__(self, queue_options, outputdir, workdir, overwrite)

        self._executable = get_settings().casino3.exe
        if not os.path.isfile(self._executable):
            raise IOError('Casino 3 executable (%s) cannot be found' % self._executable)
        logging.debug('Casino 3 executable: %s', self._executable)

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
        pass
#        dirpath = self._get_dirpath(options)
#
#        resultdirs = [name for name in os.listdir(dirpath) \
#                      if os.path.isdir(os.path.join(dirpath, name)) ]
#        resultdirs.sort()
#        if not resultdirs:
#            raise IOError, 'Cannot find results directories in %s' % dirpath
#
#        # Import results to pyMonteCarlo
#        logging.debug('Importing results from WinXRay')
#        path = os.path.join(dirpath, resultdirs[-1]) # Take last result folder
#        results = Importer().import_from_dir(options, path)
#        results.save(zipfilepath)
#
#        # Append all WinXRay results in zip
#        logging.debug('Appending all WinXRay results')
#        zip = ZipFile(zipfilepath, 'a', compression=ZIP_DEFLATED)
#
#        for filename in os.listdir(path):
#            filepath = os.path.join(path, filename)
#            arcname = "raw/%s" % filename
#            zip.write(filepath, arcname)
#
#        zip.close()
