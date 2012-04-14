#!/usr/bin/env python
"""
================================================================================
:mod:`nistmonte` -- NISTMonte Monte Carlo program
================================================================================

.. module:: nistmonte
   :synopsis: NISTMonte Monte Carlo program

.. inheritance-diagram:: pymontecarlo.program.nistmonte

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
from pymontecarlo.program.nistmonte.input.converter import Converter
from pymontecarlo.program.nistmonte.runner.worker import Worker

# Globals and constants variables.

class _NISTMonteProgram(_Program):

    def get_name(self):
        return 'NISTMonte'

    def get_alias(self):
        return 'nistmonte'

    def is_valid(self):
        try:
            java = settings.nistmonte.java
            jar = settings.nistmonte.jar
        except AttributeError:
            return False

        return os.path.isfile(java) and os.path.isfile(jar)

    def get_converter(self):
        return Converter

    def get_worker(self):
        return Worker

Program = _NISTMonteProgram()
