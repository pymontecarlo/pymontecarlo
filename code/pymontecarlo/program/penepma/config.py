#!/usr/bin/env python
"""
================================================================================
:mod:`penepma` -- PENEPMA Monte Carlo program configuration
================================================================================

.. module:: penepma
   :synopsis: PENEPMA Monte Carlo program configuration

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
from pymontecarlo.program.penelope.config import _PenelopeProgramConfiguration
from pymontecarlo.program.penepma.input.converter import Converter
from pymontecarlo.program.penepma.io.exporter import Exporter
from pymontecarlo.program.penepma.io.importer import Importer
from pymontecarlo.program.penepma.runner.worker import Worker

# Globals and constants variables.

class _PenepmaProgramConfiguration(_PenelopeProgramConfiguration):

    def _get_name(self):
        return 'PENEPMA'

    def _get_alias(self):
        return 'penepma'

    def is_valid(self):
        if not _PenelopeProgramConfiguration.is_valid(self):
            return False

        try:
            exe = settings.penepma.exe
        except AttributeError:
            return False

        return os.path.isfile(exe)

    def _get_converter(self):
        return Converter

    def _get_exporter(self):
        return Exporter

    def _get_importer(self):
        return Importer

    def _get_worker(self):
        return Worker

config = _PenepmaProgramConfiguration()
