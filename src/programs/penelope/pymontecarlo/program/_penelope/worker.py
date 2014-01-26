#!/usr/bin/env python
"""
================================================================================
:mod:`worker` -- PENSHOWER worker
================================================================================

.. module:: worker
   :synopsis: PENSHOWER worker

.. inheritance-diagram:: pymontecarlo.program.penshower.worker

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2012 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import os
import logging
import shutil
from zipfile import ZipFile

# Third party modules.

# Local modules.
from pymontecarlo.program.worker import SubprocessWorker as _Worker

# Globals and constants variables.
from zipfile import ZIP_DEFLATED

class Worker(_Worker):

    def __init__(self, program):
        """
        Runner to run PENSHOWER simulation(s).
        """
        _Worker.__init__(self, program)

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

        return _Worker.create(self, options, simdir, *args, **kwargs)

    def _extract_results(self, options, outputdir, workdir, exceptions=None):
        if exceptions is None:
            exceptions = []

        # Import results to pyMonteCarlo
        self._status = 'Importing results'
        results = self._importer.import_(options, workdir)

        # Create ZIP with all results
        zipfilepath = os.path.join(outputdir, options.name + '.zip')
        with ZipFile(zipfilepath, 'w', compression=ZIP_DEFLATED) as zipfile:
            for filename in os.listdir(workdir):
                if filename in exceptions:
                    continue
                filepath = os.path.join(workdir, filename)
                zipfile.write(filepath, filename)

        return results
