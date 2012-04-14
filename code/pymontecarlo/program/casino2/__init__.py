#!/usr/bin/env python
"""
================================================================================
:mod:`casino2` -- Casino 2 Monte Carlo program
================================================================================

.. module:: casino2
   :synopsis: Casino 2 Monte Carlo program

.. inheritance-diagram:: pymontecarlo.program.casino2

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
from pymontecarlo.program import Program as _Program
from pymontecarlo.program.casino2.input.converter import Converter
from pymontecarlo.program.casino2.io.exporter import Exporter
from pymontecarlo.program.casino2.io.importer import Importer
from pymontecarlo.program.casino2.runner.worker import Worker

# Globals and constants variables.

class _CasinoProgram(_Program):

    def get_name(self):
        return 'Casino 2'

    def get_alias(self):
        return 'casino2'

    def is_valid(self):
        try:
            exe = settings.casino2.exe
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

Program = _CasinoProgram()
