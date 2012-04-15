#!/usr/bin/env python
"""
================================================================================
:mod:`nistmonte` -- NISTMonte Monte Carlo program configuration
================================================================================

.. module:: nistmonte
   :synopsis: NISTMonte Monte Carlo program configuration

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
from pymontecarlo.program.config import ProgramConfiguration
from pymontecarlo.program.nistmonte.input.converter import Converter
from pymontecarlo.program.nistmonte.runner.worker import Worker

# Globals and constants variables.

class _NISTMonteProgramConfiguration(ProgramConfiguration):

    def _get_name(self):
        return 'NISTMonte'

    def _get_alias(self):
        return 'nistmonte'

    def is_valid(self):
        try:
            java = settings.nistmonte.java
            jar = settings.nistmonte.jar
        except AttributeError:
            return False

        return os.path.isfile(java) and os.path.isfile(jar)

    def _get_converter(self):
        return Converter

    def _get_worker(self):
        return Worker

config = _NISTMonteProgramConfiguration()
