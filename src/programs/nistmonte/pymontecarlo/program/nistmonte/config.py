#!/usr/bin/env python
"""
================================================================================
:mod:`config` -- NISTMonte Monte Carlo program configuration
================================================================================

.. module:: config
   :synopsis: NISTMonte Monte Carlo program configuration

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
from pymontecarlo.program.nistmonte.input.converter import Converter
from pymontecarlo.program.nistmonte.runner.worker import Worker

# Globals and constants variables.

class _NISTMonteProgram(Program):

    def __init__(self):
        Program.__init__(self, 'NISTMonte', 'nistmonte', Converter, Worker)

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

program = _NISTMonteProgram()