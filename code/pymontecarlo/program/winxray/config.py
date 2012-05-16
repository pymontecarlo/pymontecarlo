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
from pymontecarlo import get_settings
from pymontecarlo.program.config import Program
from pymontecarlo.program.winxray.input.converter import Converter
from pymontecarlo.program.winxray.io.exporter import Exporter
from pymontecarlo.program.winxray.io.importer import Importer
from pymontecarlo.program.winxray.runner.worker import Worker

# Globals and constants variables.
from pymontecarlo.program.config import TYPE_FILE

class _WinXRayProgram(Program):

    def _get_name(self):
        return 'WinXRay'

    def _get_alias(self):
        return 'winxray'

    def validate(self):
        settings = get_settings()

        if 'winxray' not in settings:
            raise AssertionError, "Missing 'winxray' section in settings"

        if 'exe' not in settings.winxray:
            raise AssertionError, "Missing 'exe' option in 'winxray' section of settings"

        exe = settings.winxray.exe
        if not os.path.isfile(exe):
            raise AssertionError, "Specified WinXRay executable (%s) does not exist" % exe

    def _get_converter(self):
        return Converter

    def _get_exporter(self):
        return Exporter

    def _get_importer(self):
        return Importer

    def _get_worker(self):
        return Worker

    def _get_configure_params(self):
        return [('winxray', 'exe', 'Full path to WinXRay.exe', TYPE_FILE)]

program = _WinXRayProgram()
