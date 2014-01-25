#!/usr/bin/env python
"""
================================================================================
:mod:`config` -- Casino 2 Monte Carlo program configuration
================================================================================

.. module:: config
   :synopsis: Casino 2 Monte Carlo program configuration

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
from pymontecarlo.settings import get_settings
from pymontecarlo.program.config import Program
from pymontecarlo.program.casino2.converter import Converter
from pymontecarlo.program.casino2.exporter import Exporter
from pymontecarlo.program.casino2.importer import Importer
from pymontecarlo.program.casino2.worker import Worker

# Globals and constants variables.

class _CasinoProgram(Program):

    def __init__(self):
        Program.__init__(self, 'Casino 2', 'casino2', Converter, Worker,
                          Exporter, Importer)

    def validate(self):
        settings = get_settings()

        if 'casino2' not in settings:
            raise AssertionError("Missing 'casino2' section in settings")

        if 'exe' not in settings.casino2:
            raise AssertionError("Missing 'exe' option in 'casino2' section of settings")

        exe = settings.casino2.exe
        if not os.path.isfile(exe):
            raise AssertionError("Specified Casino 2 executable (%s) does not exist" % exe)
        if not os.access(exe, os.X_OK):
            raise AssertionError("Specified Casino 2 executable (%s) is not executable" % exe)

program = _CasinoProgram()
