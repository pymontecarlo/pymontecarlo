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
from pymontecarlo.program.pap.runner.worker import Worker

# Globals and constants variables.

class _PAPProgram(_PouchouProgram):

    def _get_name(self):
        return 'PAP'

    def _get_alias(self):
        return 'pap'

    def _get_worker(self):
        return Worker

program = _PAPProgram()
