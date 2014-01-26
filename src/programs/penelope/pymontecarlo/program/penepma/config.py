#!/usr/bin/env python
"""
================================================================================
:mod:`config` -- PENEPMA Monte Carlo program configuration
================================================================================

.. module:: config
   :synopsis: PENEPMA Monte Carlo program configuration

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
from pymontecarlo.program.penepma.converter import Converter
from pymontecarlo.program.penepma.exporter import Exporter
from pymontecarlo.program.penepma.importer import Importer
from pymontecarlo.program.penepma.worker import Worker

# Globals and constants variables.

class _PenepmaProgram(_PenelopeProgram):

    def __init__(self):
        _PenelopeProgram.__init__(self, 'PENEPMA', 'penepma',
                                  Converter, Worker, Exporter, Importer)

    def validate(self):
        _PenelopeProgram.validate(self)

        settings = get_settings()

        if 'penepma' not in settings:
            raise AssertionError("Missing 'penepma' section in settings")

        if 'exe' not in settings.penepma:
            raise AssertionError("Missing 'exe' option in 'penepma' section of settings")

        pendbase = settings.penepma.pendbase
        if not os.path.isdir(pendbase):
            raise AssertionError("Specified PENELOPE pendbase directory (%s) does not exist" % pendbase)

        exe = settings.penepma.exe
        if not os.path.isfile(exe):
            raise AssertionError("Specified PENEPMA executable (%s) does not exist" % exe)
        if not os.access(exe, os.X_OK):
            raise AssertionError("Specified PENEPMA executable (%s) is not executable" % exe)

program = _PenepmaProgram()
