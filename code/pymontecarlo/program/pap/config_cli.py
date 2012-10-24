#!/usr/bin/env python
"""
================================================================================
:mod:`config_cli` -- PAP Monte Carlo program CLI configuration
================================================================================

.. module:: config_cli
   :synopsis: PAP Monte Carlo program CLI configuration

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
from pymontecarlo.program.config_cli import CLI

# Globals and constants variables.

class _PAPCLI(CLI):
    pass

cli = _PAPCLI()
