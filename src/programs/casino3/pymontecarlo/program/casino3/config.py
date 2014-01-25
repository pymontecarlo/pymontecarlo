#!/usr/bin/env python
"""
================================================================================
:mod:`config` -- Casino 3 Monte Carlo program configuration
================================================================================

.. module:: config
   :synopsis: Casino 3 Monte Carlo program configuration

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
from pymontecarlo.program.casino3.converter import Converter
#from pymontecarlo.program.casino3.exporter import Exporter
from pymontecarlo.program.casino3.importer import Importer
from pymontecarlo.program.casino3.worker import Worker

# Globals and constants variables.

class _Casino3Program(Program):

    def __init__(self):
        Program.__init__(self, 'Casino 3', 'casino3', Converter, Worker,
                          importer_class=Importer)

    def validate(self):
        settings = get_settings()

        if 'casino3' not in settings:
            raise AssertionError("Missing 'casino3' section in settings")

        if 'exe' not in settings.casino3:
            raise AssertionError("Missing 'exe' option in 'casino3' section of settings")

        exe = settings.casino3.exe
        if not os.path.isfile(exe):
            raise AssertionError("Specified Casino 3 executable (%s) does not exist" % exe)

program = _Casino3Program()
