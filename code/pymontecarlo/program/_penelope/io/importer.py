#!/usr/bin/env python
"""
================================================================================
:mod:`importer` -- Base importer for PENELOPE main programs
================================================================================

.. module:: importer
   :synopsis: Base importer for PENELOPE main programs

.. inheritance-diagram:: pymontecarlo.program._penelope.io.importer

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2012 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import os

# Third party modules.

# Local modules.
from pymontecarlo.io.importer import \
    Importer as _Importer, ImporterException, ImporterWarning #@UnusedImport

# Globals and constants variables.

class Importer(_Importer):

    def __init__(self):
        _Importer.__init__(self)

    def import_from_dir(self, options, path):
        """
        Imports PENELOPE results from a results directory.
        
        :arg options: options of the simulation
        :type options: :class:`Options <pymontecarlo.input.base.options.Options>`
        
        :arg path: location of the results directory
        """
        if not os.path.isdir(path):
            raise ValueError, "Specified path (%s) is not a directory" % path

        return self._import_results(options, path)
