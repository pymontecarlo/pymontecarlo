#!/usr/bin/env python
"""
================================================================================
:mod:`material` -- Create PENELOPE's material file
================================================================================

.. module:: material
   :synopsis: Create PENELOPE's material

.. inheritance-diagram:: pymontecarlo.lib.penelope.material

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
from pymontecarlo import settings
from _material import create as _create #@UnresolvedImport

# Globals and constants variables.

def create(mat, filepath):
    oldcwd = os.getcwd()
    os.chdir(settings.penelope.pendbase)

    _create(mat, filepath)

    os.chdir(oldcwd)
