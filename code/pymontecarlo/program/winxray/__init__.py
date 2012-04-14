#!/usr/bin/env python
"""
================================================================================
:mod:`winxray` -- WinXRay Monte Carlo program
================================================================================

.. module:: winxray
   :synopsis: WinXRay Monte Carlo program

.. inheritance-diagram:: pymontecarlo.program.winxray

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
from pymontecarlo.program.winxray.input.converter import Converter
from pymontecarlo.program.winxray.io.exporter import Exporter
from pymontecarlo.program.winxray.io.importer import Importer
from pymontecarlo.program.winxray.runner.worker import Worker

# Globals and constants variables.

class _WinXRayProgram(_Program):

    def get_name(self):
        return 'WinXRay'

    def get_alias(self):
        return 'winxray'

    def is_valid(self):
        try:
            exe = settings.winxray.exe
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

Program = _WinXRayProgram()
