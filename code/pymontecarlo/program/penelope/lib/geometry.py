#!/usr/bin/env python
"""
================================================================================
:mod:`geometry` -- Access to PENELOPE's PENGEOM methods
================================================================================

.. module:: geometry
   :synopsis: Access to PENELOPE's PENGEOM methods

.. inheritance-diagram:: pymontecarlo.lib.penelope.geometry

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
from pymontecarlo.program.penelope.lib._geometry import init as _init #@UnresolvedImport

# Globals and constants variables.

def init(geofilepath, repfilepath=None):
    """
    Initializes the geometry and returns the number of materials and bodies.
    
    :arg geofilepath: location of the .geo file.
    :arg repfilepath: location where to save the .rep file created when 
        initializing the geometry. If ``None``, the .rep file is saved in the 
        same directory as the *geofilepath*.
        
    :return: number of materials and bodies
    """
    if repfilepath is None:
        repfilepath = os.path.splitext(geofilepath)[0] + ".rep"

    return _init(geofilepath, repfilepath)
