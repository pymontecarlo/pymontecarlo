#!/usr/bin/env python
"""
================================================================================
:mod:`config` -- WinXRay Monte Carlo program configuration
================================================================================

.. module:: config
   :synopsis: WinXRay Monte Carlo program configuration

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
from pymontecarlo.program.winxray.converter import Converter
from pymontecarlo.program.winxray.exporter import Exporter
from pymontecarlo.program.winxray.importer import Importer
from pymontecarlo.program.winxray.worker import Worker

# Globals and constants variables.

class _WinXRayProgram(Program):

    def __init__(self):
        Program.__init__(self, 'WinXRay', 'winxray', Converter, Worker,
                          Exporter, Importer)

    def validate(self):
        settings = get_settings()

        if 'winxray' not in settings:
            raise AssertionError("Missing 'winxray' section in settings")

        if 'exe' not in settings.winxray:
            raise AssertionError("Missing 'exe' option in 'winxray' section of settings")

        exe = settings.winxray.exe
        if not os.path.isfile(exe):
            raise AssertionError("Specified WinXRay executable (%s) does not exist" % exe)
        if not os.access(exe, os.X_OK):
            raise AssertionError("Specified WinXRay executable (%s) is not executable" % exe)

program = _WinXRayProgram()
