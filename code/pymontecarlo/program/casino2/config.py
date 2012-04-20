#!/usr/bin/env python
"""
================================================================================
:mod:`casino2` -- Casino 2 Monte Carlo program configuration
================================================================================

.. module:: casino2
   :synopsis: Casino 2 Monte Carlo program configuration

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
from pymontecarlo.program.config import Program
from pymontecarlo.program.casino2.input.converter import Converter
from pymontecarlo.program.casino2.io.exporter import Exporter
from pymontecarlo.program.casino2.io.importer import Importer
from pymontecarlo.program.casino2.runner.worker import Worker

# Globals and constants variables.

class _CasinoProgram(Program):

    def _get_name(self):
        return 'Casino 2'

    def _get_alias(self):
        return 'casino2'

    def _get_converter(self):
        return Converter

    def _get_exporter(self):
        return Exporter

    def _get_importer(self):
        return Importer

    def _get_worker(self):
        return Worker

    def validate(self):
        if 'casino2' not in settings:
            raise AssertionError, "Missing 'casino2' section in settings"

        if 'exe' not in settings.casino2:
            raise AssertionError, "Missing 'exe' option in 'casino2' section of settings"

        exe = settings.casino2.exe
        if not os.path.isfile(exe):
            raise AssertionError, "Specified Casino 2 executable (%s) does not exist" % exe

program = _CasinoProgram()
