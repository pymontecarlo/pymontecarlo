#!/usr/bin/env python
"""
================================================================================
:mod:`penepma` -- PENEPMA Monte Carlo program
================================================================================

.. module:: penepma
   :synopsis: PENEPMA Monte Carlo program

.. inheritance-diagram:: pymontecarlo.program.penepma

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
from pymontecarlo import settings
from pymontecarlo.program.penelope import _PenelopeProgram
from pymontecarlo.program.penepma.input.converter import Converter
from pymontecarlo.program.penepma.io.exporter import Exporter
from pymontecarlo.program.penepma.io.importer import Importer
from pymontecarlo.program.penepma.runner.worker import Worker

# Globals and constants variables.

class _PenepmaProgram(_PenelopeProgram):

    def get_name(self):
        return 'PENEPMA'

    def get_alias(self):
        return 'penepma'

    def is_valid(self):
        _PenelopeProgram.is_valid(self)

        try:
            exe = settings.penepma.exe
        except AttributeError:
            return False

        return os.path.isfile(exe)

    def get_converter(self):
        return Converter

    def get_exporter(self):
        return Exporter

    def get_importer(self):
        return Importer

    def get_worker(self):
        return Worker

Program = _PenepmaProgram()
