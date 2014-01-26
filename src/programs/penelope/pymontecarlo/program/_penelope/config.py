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

# Third party modules.

# Local modules.
from pymontecarlo.program.config import Program

# Globals and constants variables.

# Load submodules to register XML loader and saver

class _PenelopeProgram(Program):
    pass
