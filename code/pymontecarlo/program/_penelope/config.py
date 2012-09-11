#!/usr/bin/env python
"""
================================================================================
:mod:`config` -- PENELOPE Monte Carlo program configuration
================================================================================

.. module:: config
   :synopsis: PENELOPE Monte Carlo program configuration

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

# Globals and constants variables.

# Load submodules to register XML loader and saver
import pymontecarlo.program._penelope.input.body #@UnusedImport
import pymontecarlo.program._penelope.input.material #@UnusedImport

class _PenelopeProgram(Program):

    def validate(self):
        settings = get_settings()

        if 'penelope' not in settings:
            raise AssertionError, "Missing 'penelope' section in settings"

        if 'pendbase' not in settings.penelope:
            raise AssertionError, "Missing 'pendbase' option in 'penelope' section of settings"

        pendbase = settings.penelope.pendbase
        if not os.path.isdir(pendbase):
            raise AssertionError, "Specified PENELOPE pendbase directory (%s) does not exist" % pendbase

