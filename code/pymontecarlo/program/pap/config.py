#!/usr/bin/env python
"""
================================================================================
:mod:`config` -- PAP Monte Carlo program configuration
================================================================================

.. module:: config
   :synopsis: PAP Monte Carlo program configuration

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
from pymontecarlo.program.pap.runner.worker import Worker

# Globals and constants variables.

class _PAPProgram(Program):

    def __init__(self):
        Program.__init__(self, 'PAP', 'pap', Converter, Worker)

program = _PAPProgram()
