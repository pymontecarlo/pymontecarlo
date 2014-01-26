#!/usr/bin/env python
"""
================================================================================
:mod:`config` -- PENSHOWER Monte Carlo program configuration
================================================================================

.. module:: config
   :synopsis: PENSHOWER Monte Carlo program configuration

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
from pymontecarlo.program._penelope.config import _PenelopeProgram
from pymontecarlo.program.penshower.converter import Converter
from pymontecarlo.program.penshower.exporter import Exporter
from pymontecarlo.program.penshower.importer import Importer
from pymontecarlo.program.penshower.worker import Worker

# Globals and constants variables.

class _PenshowerProgram(_PenelopeProgram):

    def __init__(self):
        _PenelopeProgram.__init__(self, 'PENSHOWER', 'penshower',
                                  Converter, Worker, Exporter, Importer)

    def validate(self):
        _PenelopeProgram.validate(self)

        settings = get_settings()

        if 'penshower' not in settings:
            raise AssertionError("Missing 'penshower' section in settings")

        if 'exe' not in settings.penshower:
            raise AssertionError("Missing 'exe' option in 'penshower' section of settings")

        pendbase = settings.penshower.pendbase
        if not os.path.isdir(pendbase):
            raise AssertionError("Specified PENELOPE pendbase directory (%s) does not exist" % pendbase)

        exe = settings.penshower.exe
        if not os.path.isfile(exe):
            raise AssertionError("Specified PENSHOWER executable (%s) does not exist" % exe)
        if not os.access(exe, os.X_OK):
            raise AssertionError("Specified PENSHOWER executable (%s) is not executable" % exe)

program = _PenshowerProgram()
