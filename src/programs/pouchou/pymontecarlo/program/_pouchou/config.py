#!/usr/bin/env python
"""
================================================================================
:mod:`config` -- Pouchou programs configuration
================================================================================

.. module:: config
   :synopsis: Pouchou program configuration

.. inheritance-diagram:: pymontecarlo.program._pouchou.config

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2012 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.input.exporter import XMLExporter
from pymontecarlo.output.importer import HDF5Importer
from pymontecarlo.program.config import Program
from pymontecarlo.program._pouchou.input.converter import Converter

# Globals and constants variables.

class _PouchouProgram(Program):

    def __init__(self, name, alias, worker_class):
        Program.__init__(self, name, alias,
                         Converter, worker_class, XMLExporter, HDF5Importer)

