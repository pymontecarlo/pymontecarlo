#!/usr/bin/env python
"""
================================================================================
:mod:`pymontecarlo` -- Common interface to several Monte Carlo codes
================================================================================

.. module:: pymontecarlo
   :synopsis: Common interface to several Monte Carlo codes

.. inheritance-diagram:: pymontecarlo

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2011 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import os

# Third party modules.

# Local modules.
from pymontecarlo.util.config import ConfigReader

# Globals and constants variables.

settings = ConfigReader()

__filepath = os.path.join(os.path.dirname(__file__), 'settings.cfg')
if os.path.exists(__filepath):
    with open(__filepath, 'r') as f:
        settings.read(f)
