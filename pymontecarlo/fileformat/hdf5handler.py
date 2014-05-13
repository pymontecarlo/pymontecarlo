#!/usr/bin/env python
"""
================================================================================
:mod:`hdf5handler` -- Handler to load and save from HDF5
================================================================================

.. module:: hdf5handler
   :synopsis: Handler to load and save from HDF5

.. inheritance-diagram:: pymontecarlo.fileformat.hdf5handler

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2014 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.

# Third party modules.
import numpy as np

# Local modules.
from pymontecarlo.fileformat.handler import _Handler

# Globals and constants variables.

class _HDF5Handler(_Handler):

    CLASS = None

    def can_parse(self, group):
        return group.attrs['_class'] == np.string_(self.CLASS.__name__)

    def parse(self, group):
        return self.CLASS()

    def convert(self, obj, group):
        group.attrs['_class'] = np.string_(self.CLASS.__name__)
        return group
