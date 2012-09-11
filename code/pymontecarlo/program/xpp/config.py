#!/usr/bin/env python
"""
================================================================================
:mod:`config` -- XPP Monte Carlo program configuration
================================================================================

.. module:: config
   :synopsis: XPP Monte Carlo program configuration

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
from pymontecarlo.program._pouchou.input.converter import Converter
from pymontecarlo.program.xpp.runner.worker import Worker

# Globals and constants variables.

class _XPPProgram(Program):

    def __init__(self):
        Program.__init__(self, 'XPP', 'xpp', Converter, Worker)

program = _XPPProgram()
