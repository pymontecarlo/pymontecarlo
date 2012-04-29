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
from pymontecarlo import get_settings
from pymontecarlo.program.config import Program
from pymontecarlo.program.nistmonte.input.converter import Converter
from pymontecarlo.program.nistmonte.runner.worker import Worker

# Globals and constants variables.
from pymontecarlo.program.config import TYPE_FILE

class _NISTMonteProgram(Program):

    def _get_name(self):
        return 'NISTMonte'

    def _get_alias(self):
        return 'nistmonte'

    def validate(self):
        settings = get_settings()

        if 'nistmonte' not in settings:
            raise AssertionError, "Missing 'nistmonte' section in settings"

        if 'java' not in settings.nistmonte:
            raise AssertionError, "Missing 'java' option in 'nistmonte' section of settings"

        java = settings.nistmonte.java
        if not os.path.isfile(java):
            raise AssertionError, "Specified Java executable (%s) does not exist" % java

        if 'jar' not in settings.nistmonte:
            raise AssertionError, "Missing 'jar' option in 'nistmonte' section of settings"

        jar = settings.nistmonte.jar
        if not os.path.isfile(jar):
            raise AssertionError, "Specified jar path (%s) does not exist" % jar

    def _get_converter(self):
        return Converter

    def _get_worker(self):
        return Worker

    def _get_configure_params(self):
        return [('nistmonte', 'java', 'Path to Java executable', TYPE_FILE),
                ('nistmonte', 'jar', 'Path to NISTMonte jar', TYPE_FILE)]

program = _NISTMonteProgram()
