#!/usr/bin/env python
"""
================================================================================
:mod:`importer` -- Monaco results importer
================================================================================

.. module:: importer
   :synopsis: Monaco results importer

.. inheritance-diagram:: pymontecarlo.program.monaco.io.importer

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2011 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.io.importer import Importer as _Importer

# Globals and constants variables.

class Importer(_Importer):

    def __init__(self):
        _Importer.__init__(self)




