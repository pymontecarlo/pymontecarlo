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
from pymontecarlo.program._pouchou.config import _PouchouProgram
from pymontecarlo.program.xpp.runner.worker import Worker

# Globals and constants variables.

class _PAPProgram(_PouchouProgram):

    def __init__(self):
        _PouchouProgram.__init__(self, 'PAP', 'pap', Worker)

program = _PAPProgram()
