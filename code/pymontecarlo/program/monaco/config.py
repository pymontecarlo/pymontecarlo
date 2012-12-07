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
from pymontecarlo import get_settings
from pymontecarlo.program.config import Program
from pymontecarlo.program.monaco.input.converter import Converter
from pymontecarlo.program.monaco.io.exporter import Exporter
from pymontecarlo.program.monaco.io.importer import Importer
from pymontecarlo.program.monaco.runner.worker import Worker

# Globals and constants variables.

class _MonacoProgram(Program):

    def __init__(self):
        Program.__init__(self, 'Monaco', 'monaco', Converter, Worker,
                          Exporter, Importer)

    def validate(self):
        settings = get_settings()

        if 'monaco' not in settings:
            raise AssertionError, "Missing 'monaco' section in settings"

        if 'basedir' not in settings.monaco:
            raise AssertionError, "Missing 'basedir' option in 'monaco' section of settings"

        basedir = settings.monaco.basedir
        if not os.path.isdir(basedir):
            raise AssertionError, "Specified Monaco base directory (%s) does not exist" % basedir

        mcsim32_exe = os.path.join(settings.monaco.basedir, 'Mcsim32.exe')
        if not os.path.isfile(mcsim32_exe):
            raise AssertionError, "No Mcsim32.exe in Monaco base directory (%s)" % basedir

        mccorr32_exe = os.path.join(settings.monaco.basedir, 'Mccorr32.exe')
        if not os.path.isfile(mccorr32_exe):
            raise AssertionError, "No Mccorr32.exe in Monaco base directory (%s)" % basedir

program = _MonacoProgram()
