#!/usr/bin/env python
"""
================================================================================
:mod:`penelope` -- PENELOPE Monte Carlo program
================================================================================

.. module:: penelope
   :synopsis: PENELOPE Monte Carlo program

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

# Globals and constants variables.
from pymontecarlo.util.xmlutil import XMLIO


XMLIO.register_namespace('mc-pen', 'http://pymontecarlo.sf.net/penelope')
